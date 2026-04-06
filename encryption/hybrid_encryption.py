import os
import json
import threading
import multiprocessing
import time
import psutil
from concurrent.futures import ThreadPoolExecutor
from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import pad, unpad
from .quantum_key import QuantumKeyGenerator
from .anti_quantum_alg import AntiQuantumAlgorithm
from utils.memory_cleaner import clear_memory, clear_sensitive_data

# 自定义异常类
class DecryptionError(Exception):
    """解密失败的基类异常"""
    pass

class PaddingError(DecryptionError):
    """填充验证失败异常"""
    pass

class InvalidCiphertextError(DecryptionError):
    """无效密文异常"""
    pass

class HybridEncryption:
    """
    混合加密模块，实现三层加密架构
    """
    
    def __init__(self):
        """
        初始化混合加密模块
        """
        self.quantum_key_gen = QuantumKeyGenerator()
        self.anti_quantum_alg = AntiQuantumAlgorithm()
        # 调整分块大小，根据系统内存情况动态调整
        # 对于大多数系统，4MB分块大小可以提供更好的性能
        self.block_size = 4 * 1024 * 1024  # 4MB分块大小
        # 根据系统CPU核心数动态调整最大线程数
        # 计算最佳线程数：CPU核心数的1.5倍，至少4个线程
        cpu_count = multiprocessing.cpu_count()
        self.max_threads = max(4, min(32, int(cpu_count * 1.5)))  # 最多32个线程，避免过度线程切换
        # 创建线程池，避免频繁创建和销毁线程
        # 优化：设置线程池的线程名称前缀，便于调试
        self.executor = ThreadPoolExecutor(max_workers=self.max_threads, thread_name_prefix="FCFS-Worker")
        # 优化：添加内存使用监控和限制
        self.memory_limit = None  # 内存使用限制，默认无限制
        # 优化：添加任务队列监控
        self.active_tasks = 0
    
    def generate_session_key(self, master_key, key_length=128):
        """
        生成会话密钥
        
        Args:
            master_key (bytes): 主密钥
            key_length (int, optional): 密钥长度（字节），默认128字节
        
        Returns:
            tuple: (量子密钥密文, 会话密钥)
        """
        try:
            # 生成量子密钥
            quantum_key = self.quantum_key_gen.generate_quantum_key(key_length)
            
            # 使用简单的接收方公钥（实际应用中应使用真正的公钥）
            # 这里使用master_key的前64字节作为模拟公钥
            receiver_public_key = master_key[:64]
            
            # 封装量子密钥
            quantum_key_cipher = self.quantum_key_gen.encapsulate_key(quantum_key, receiver_public_key)
            
            # 生成会话密钥
            session_key = self.quantum_key_gen.generate_session_key(quantum_key, master_key)
            
            return (quantum_key_cipher, session_key)
        except Exception as e:
            raise RuntimeError(f"会话密钥生成失败: {str(e)}")
    
    def aes_encrypt(self, data, key):
        """
        使用AES-512算法加密数据
        
        Args:
            data (bytes): 待加密数据
            key (bytes): 加密密钥
        
        Returns:
            bytes: 加密后的数据
        """
        try:
            # AES-256需要32字节密钥
            key = key[:32] if len(key) > 32 else key.ljust(32, b'\x00')
            
            # 生成随机IV
            iv = os.urandom(16)
            
            # 创建AES加密器
            cipher = AES.new(key, AES.MODE_CBC, iv)
            
            # 加密数据
            padded_data = pad(data, AES.block_size)
            ciphertext = cipher.encrypt(padded_data)
            
            # 返回IV+密文
            return iv + ciphertext
        except Exception as e:
            raise RuntimeError(f"AES-512加密失败: {str(e)}")
    
    def sm4_encrypt(self, data, key):
        """
        使用AES算法模拟SM4-512算法加密数据
        
        Args:
            data (bytes): 待加密数据
            key (bytes): 加密密钥
        
        Returns:
            bytes: 加密后的数据
        """
        try:
            # SM4需要16字节密钥，使用AES-128模拟
            key = key[:16] if len(key) > 16 else key.ljust(16, b'\x00')
            
            # 生成随机IV
            iv = os.urandom(16)
            
            # 创建AES加密器（模拟SM4）
            cipher = AES.new(key, AES.MODE_CBC, iv)
            
            # 加密数据，SM4的块大小也是16字节，与AES相同
            padded_data = pad(data, AES.block_size)
            ciphertext = cipher.encrypt(padded_data)
            
            # 返回IV+密文
            return iv + ciphertext
        except Exception as e:
            raise RuntimeError(f"SM4-512加密失败: {str(e)}")
    
    def _encrypt_chunk(self, chunk, session_key):
        """
        加密单个数据块
        
        Args:
            chunk (bytes): 数据块
            session_key (bytes): 会话密钥
        
        Returns:
            bytes: 加密后的数据块
        """
        # 第一层：AES加密
        c1 = self.aes_encrypt(chunk, session_key)
        # 第二层：SM4加密
        c2 = self.sm4_encrypt(c1, session_key)
        # 第三层：抗量子算法加密
        c3 = self.anti_quantum_alg.encrypt(c2)
        return c3
    
    def generate_signature(self, data, private_key):
        """
        生成数字签名
        
        Args:
            data (bytes): 待签名数据
            private_key (bytes): 用户私钥
        
        Returns:
            bytes: 数字签名
        """
        # 这里使用简单的哈希值作为模拟签名
        # 实际应用中应使用真正的数字签名算法，如RSA或ECC
        from hashlib import sha512
        
        # 使用私钥和数据生成哈希值作为签名
        signature_data = private_key + data
        signature = sha512(signature_data).digest()
        
        return signature
    
    def encrypt(self, compressed_file, master_key, output_file=None, sha512_hash=None, sm3_hash=None):
        """
        执行混合加密
        
        Args:
            compressed_file (str): 压缩包路径
            master_key (bytes): 主密钥
            output_file (str, optional): 输出加密包路径，默认在当前目录生成
            sha512_hash (str, optional): 压缩包的SHA-512哈希值，若不提供则重新计算
            sm3_hash (str, optional): 压缩包的SM3哈希值，若不提供则重新计算
        
        Returns:
            tuple: (加密包路径, sha512_hash, sm3_hash)
        """
        try:
            # 获取压缩包的哈希值，如果未提供则重新计算
            from utils.hash_calculator import calculate_hash_pair
            if not sha512_hash or not sm3_hash:
                sha512_hash, sm3_hash = calculate_hash_pair(compressed_file)
            
            # 1. 第一层：量子密钥生成与封装
            print("开始第一层加密：量子密钥生成与封装")
            quantum_key_cipher, session_key = self.generate_session_key(master_key)
            print("✓ 会话密钥生成完成")
            
            # 2. 边读边加密，减少内存占用
            print("开始读取文件并分块加密...")
            # 使用缓冲区读取文件，提高I/O性能
            buffer_size = 8 * 1024 * 1024  # 8MB缓冲区
            
            # 优化：添加内存使用监控，避免过度分配内存
            import psutil
            process = psutil.Process(os.getpid())
            
            # 优化：使用生成器边读边加密，减少内存占用
            def read_and_encrypt():
                """
                生成器：边读取文件边加密
                """
                chunk_index = 0
                with open(compressed_file, 'rb', buffering=buffer_size) as f:
                    while True:
                        chunk = f.read(self.block_size)
                        if not chunk:
                            break
                        
                        # 检查内存使用情况
                        memory_info = process.memory_info()
                        memory_usage = memory_info.rss / (1024 * 1024)  # MB
                        
                        # 如果内存使用超过限制，等待一段时间再继续
                        if self.memory_limit and memory_usage > self.memory_limit:
                            print(f"警告：内存使用过高 ({memory_usage:.2f} MB)，等待内存释放...")
                            time.sleep(0.1)
                        
                        yield chunk_index, chunk
                        chunk_index += 1
            
            # 3. 多线程并行加密
            print("开始第二层加密：双对称算法加密")
            encrypted_chunks = []
            lock = threading.Lock()
            chunk_count = 0
            
            # 优化：使用线程安全的方式收集加密结果
            def encrypt_worker(chunk_index, chunk):
                """
                加密单个数据块
                
                Args:
                    chunk_index (int): 块索引
                    chunk (bytes): 数据块
                """
                try:
                    encrypted_chunk = self._encrypt_chunk(chunk, session_key)
                    with lock:
                        encrypted_chunks.append((chunk_index, encrypted_chunk))
                        # 每加密10块打印一次进度
                        if (len(encrypted_chunks) % 10 == 0):
                            print(f"✓ 加密进度: {len(encrypted_chunks)}")
                except Exception as e:
                    print(f"加密块失败: {str(e)}")
                    raise
            
            # 优化：批量提交任务，减少线程池调度开销
            futures = []
            batch_size = 10
            batch = []
            
            for chunk_index, chunk in read_and_encrypt():
                batch.append((chunk_index, chunk))
                chunk_count += 1
                
                if len(batch) >= batch_size:
                    # 提交当前批次
                    for item in batch:
                        future = self.executor.submit(encrypt_worker, item[0], item[1])
                        futures.append(future)
                    batch = []
            
            # 提交剩余批次
            if batch:
                for item in batch:
                    future = self.executor.submit(encrypt_worker, item[0], item[1])
                    futures.append(future)
            
            # 等待所有任务完成
            for future in futures:
                future.result()  # 等待任务完成并获取结果
            
            print(f"✓ 双对称算法加密完成，共{chunk_count}块")
            
            # 4. 按索引排序并整合加密结果
            print("开始整合加密结果...")
            # 按索引排序加密块
            encrypted_chunks.sort(key=lambda x: x[0])
            # 提取加密数据
            c3 = b''.join([chunk[1] for chunk in encrypted_chunks])
            
            # 5. 数字签名生成
            print("开始生成数字签名")
            # 使用master_key作为模拟私钥
            signature = self.generate_signature(c3 + sha512_hash.encode() + sm3_hash.encode(), master_key)
            print("✓ 数字签名生成完成")
            
            # 6. 加密包整合
            print("开始整合加密包")
            
            # 生成输出文件路径
            if not output_file:
                output_file = os.path.join(os.path.dirname(compressed_file), 'File.7z.enc')
            
            # 优化：使用base64编码替代hex编码，减少数据大小
            import base64
            # 创建加密包数据结构
            encrypted_data = {
                'c3': base64.b64encode(c3).decode('utf-8'),
                'qkc': base64.b64encode(quantum_key_cipher).decode('utf-8'),
                'signature': base64.b64encode(signature).decode('utf-8'),
                'sha512': sha512_hash,
                'sm3': sm3_hash
            }
            
            # 优化：使用更高效的JSON序列化，不使用缩进
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(encrypted_data, f, ensure_ascii=False, separators=(',', ':'))
            
            print(f"✓ 加密包生成完成: {output_file}")
            
            # 清除敏感数据（优化：统一在函数结束时清理）
            # 清理临时变量
            del c3, quantum_key_cipher, session_key, encrypted_data
            
            return (output_file, sha512_hash, sm3_hash)
        except Exception as e:
            # 清理临时文件
            if output_file and os.path.exists(output_file):
                os.remove(output_file)
            raise RuntimeError(f"混合加密失败: {str(e)}")
    
    def decrypt(self, encrypted_file, master_key, output_file=None):
        """
        执行混合解密，支持失败回滚
        
        Args:
            encrypted_file (str): 加密包路径
            master_key (bytes): 主密钥
            output_file (str, optional): 输出解密文件路径，默认在当前目录生成
        
        Returns:
            str: 解密后的文件路径
        """
        # 保存输出文件路径，用于异常处理时清理
        temp_output_file = output_file or os.path.join(os.path.dirname(encrypted_file), 'Temp_File.7z')
        
        try:
            # 优化：直接读取并解析加密包，减少临时变量
            with open(encrypted_file, 'r', encoding='utf-8') as f:
                encrypted_data = json.load(f)
            
            # 解析加密包数据
            import base64
            c3 = base64.b64decode(encrypted_data['c3'])
            qkc = base64.b64decode(encrypted_data['qkc'])
            signature = base64.b64decode(encrypted_data['signature'])
            sha512_hash = encrypted_data['sha512']
            sm3_hash = encrypted_data['sm3']
            
            # 1. 验证数字签名
            expected_signature = self.generate_signature(c3 + sha512_hash.encode() + sm3_hash.encode(), master_key)
            if signature != expected_signature:
                raise RuntimeError("数字签名验证失败")
            
            # 2. 解封装量子密钥
            receiver_private_key = master_key  # 使用master_key作为模拟私钥
            quantum_key = self.quantum_key_gen.decapsulate_key(qkc, receiver_private_key)
            
            # 生成会话密钥
            session_key = self.quantum_key_gen.generate_session_key(quantum_key, master_key)
            
            # 3. 解密
            print("开始解密...")
            
            # 第一层：自定义抗量子算法解密
            print("  执行第一层解密：抗量子算法解密...")
            c2 = self.anti_quantum_alg.decrypt(c3)
            print("  ✓ 抗量子算法解密完成")
            
            # 第二层：双对称算法解密
            print("  执行第二层解密：双对称算法解密...")
            
            # 3.1 用会话密钥SK调用SM4-512逆向算法解密C2 → 还原密文C1
            # 注意：由于每个加密块都有自己的IV和填充，我们需要分块解密
            print("    执行SM4-512解密...")
            c1 = self._parallel_sm4_decrypt(c2, session_key)
            print("  ✓ SM4-512解密完成")
            
            # 3.2 用同一会话密钥SK调用AES-512逆向算法解密C1 → 还原7Z压缩包Temp_File.7z
            print("    执行AES-512解密...")
            temp_file_content = self._parallel_aes_decrypt(c1, session_key)
            print("  ✓ AES-512解密完成")
            
            print("✓ 解密完成")
            
            # 4. 整合解密结果
            print("开始整合解密结果...")
            
            # 5. 写入解密后的文件
            # 优化：使用缓冲区写入，减少I/O操作
            buffer_size = 8 * 1024 * 1024  # 8MB缓冲区
            with open(temp_output_file, 'wb', buffering=buffer_size) as f:
                f.write(temp_file_content)
            
            print(f"✓ 解密文件写入完成: {temp_output_file}")
            
            # 优化：只在函数结束前清理敏感数据，减少中间操作
            return temp_output_file
        except Exception as e:
            # 清理临时文件
            if os.path.exists(temp_output_file):
                try:
                    os.remove(temp_output_file)
                except:
                    pass
            
            raise RuntimeError(f"混合解密失败: {str(e)}")
    
    def sm4_decrypt(self, ciphertext, key):
        """
        使用AES算法模拟SM4-512算法解密数据
        
        Args:
            ciphertext (bytes): 密文数据
            key (bytes): 解密密钥
        
        Returns:
            bytes: 解密后的数据
        
        Raises:
            InvalidCiphertextError: 当密文无效或太短时
            PaddingError: 当填充验证失败时
            DecryptionError: 当解密过程中发生其他错误时
        """
        try:
            # SM4需要16字节密钥，使用AES-128模拟
            key = key[:16] if len(key) > 16 else key.ljust(16, b'\x00')
            
            # 分离IV和密文
            if len(ciphertext) < 16:
                raise InvalidCiphertextError("密文太短，无法解密")
            
            iv = ciphertext[:16]
            ciphertext = ciphertext[16:]
            
            # 如果密文长度为0，直接返回空字节
            if not ciphertext:
                return b''
            
            # 创建AES解密器（模拟SM4）
            cipher = AES.new(key, AES.MODE_CBC, iv)
            
            # 解密数据，SM4的块大小也是16字节，与AES相同
            padded_data = cipher.decrypt(ciphertext)
            
            # 验证并去除填充
            try:
                data = unpad(padded_data, AES.block_size)
            except ValueError as e:
                raise PaddingError("填充验证失败，数据可能已损坏") from e
            
            return data
        except DecryptionError:
            # 重新抛出自定义异常
            raise
        except Exception as e:
            # 将其他异常包装为DecryptionError
            raise DecryptionError(f"SM4解密失败: {str(e)}") from e
    
    def aes_decrypt(self, ciphertext, key):
        """
        使用AES-512算法解密数据
        
        Args:
            ciphertext (bytes): 密文数据
            key (bytes): 解密密钥
        
        Returns:
            bytes: 解密后的数据
        
        Raises:
            InvalidCiphertextError: 当密文无效或太短时
            PaddingError: 当填充验证失败时
            DecryptionError: 当解密过程中发生其他错误时
        """
        try:
            # AES-256需要32字节密钥
            key = key[:32] if len(key) > 32 else key.ljust(32, b'\x00')
            
            # 分离IV和密文
            if len(ciphertext) < 16:
                raise InvalidCiphertextError("密文太短，无法解密")
            
            iv = ciphertext[:16]
            ciphertext = ciphertext[16:]
            
            # 如果密文长度为0，直接返回空字节
            if not ciphertext:
                return b''
            
            # 创建AES解密器
            cipher = AES.new(key, AES.MODE_CBC, iv)
            
            # 解密数据
            padded_data = cipher.decrypt(ciphertext)
            
            # 验证并去除填充
            try:
                data = unpad(padded_data, AES.block_size)
            except ValueError as e:
                raise PaddingError("填充验证失败，数据可能已损坏") from e
            
            return data
        except DecryptionError:
            # 重新抛出自定义异常
            raise
        except Exception as e:
            # 将其他异常包装为DecryptionError
            raise DecryptionError(f"AES解密失败: {str(e)}") from e
    
    def _decrypt_single_block(self, block, decrypt_func, key):
        """
        解密单个数据块
        
        Args:
            block (bytes): 数据块
            decrypt_func (function): 解密函数
            key (bytes): 解密密钥
        
        Returns:
            bytes: 解密后的数据块
        """
        try:
            return decrypt_func(block, key)
        except Exception as e:
            raise RuntimeError(f"解密块失败: {str(e)}")
    
    def _decrypt_sm4_blocks(self, ciphertext, key):
        """
        解密SM4加密的分块数据
        
        Args:
            ciphertext (bytes): SM4加密的数据
            key (bytes): 解密密钥
        
        Returns:
            bytes: 解密后的数据
        """
        # 解密SM4加密的分块数据
        # 注意：每个块的大小是加密时的块大小加上IV大小
        # 由于抗量子算法可能改变数据长度，我们需要动态处理
        
        # 尝试不同的块大小，找到正确的分块方式
        # 常见的块大小：原始块大小 + 16字节IV
        possible_block_sizes = [self.block_size + 16, self.block_size * 2 + 16, self.block_size // 2 + 16]
        
        for block_size in possible_block_sizes:
            try:
                blocks = []
                i = 0
                while i < len(ciphertext):
                    # 找到下一个块的边界
                    # 由于每个块都有自己的IV，我们可以尝试找到有效的IV和密文
                    # 简单起见，我们使用固定的块大小进行尝试
                    next_i = i + block_size
                    if next_i > len(ciphertext):
                        next_i = len(ciphertext)
                    if next_i > i:
                        blocks.append(ciphertext[i:next_i])
                    i = next_i
                
                # 尝试解密所有块
                decrypted_blocks = []
                for block in blocks:
                    if len(block) >= 16:  # 至少需要16字节IV
                        decrypted_block = self.sm4_decrypt(block, key)
                        decrypted_blocks.append(decrypted_block)
                
                # 如果成功解密，返回结果
                if decrypted_blocks:
                    return b''.join(decrypted_blocks)
            except Exception:
                # 如果失败，尝试下一个块大小
                continue
        
        # 如果所有块大小都失败，尝试直接解密整个数据
        try:
            return self.sm4_decrypt(ciphertext, key)
        except Exception as e:
            raise RuntimeError(f"SM4分块解密失败: {str(e)}")
    
    def _decrypt_aes_blocks(self, ciphertext, key):
        """
        解密AES加密的分块数据
        
        Args:
            ciphertext (bytes): AES加密的数据
            key (bytes): 解密密钥
        
        Returns:
            bytes: 解密后的数据
        """
        # 解密AES加密的分块数据
        # 注意：每个块的大小是加密时的块大小加上IV大小
        
        # 尝试不同的块大小，找到正确的分块方式
        possible_block_sizes = [self.block_size + 16, self.block_size * 2 + 16, self.block_size // 2 + 16]
        
        for block_size in possible_block_sizes:
            try:
                blocks = []
                i = 0
                while i < len(ciphertext):
                    # 找到下一个块的边界
                    next_i = i + block_size
                    if next_i > len(ciphertext):
                        next_i = len(ciphertext)
                    if next_i > i:
                        blocks.append(ciphertext[i:next_i])
                    i = next_i
                
                # 尝试解密所有块
                decrypted_blocks = []
                for block in blocks:
                    if len(block) >= 16:  # 至少需要16字节IV
                        decrypted_block = self.aes_decrypt(block, key)
                        decrypted_blocks.append(decrypted_block)
                
                # 如果成功解密，返回结果
                if decrypted_blocks:
                    return b''.join(decrypted_blocks)
            except Exception:
                # 如果失败，尝试下一个块大小
                continue
        
        # 如果所有块大小都失败，尝试直接解密整个数据
        try:
            return self.aes_decrypt(ciphertext, key)
        except Exception as e:
            raise RuntimeError(f"AES分块解密失败: {str(e)}")
    
    def _parallel_sm4_decrypt(self, ciphertext, key):
        """
        并行解密SM4加密的数据
        
        Args:
            ciphertext (bytes): SM4加密的数据
            key (bytes): 解密密钥
        
        Returns:
            bytes: 解密后的数据
        """
        # 将SM4加密数据分块（每个块包含IV和密文）
        # 注意：这里的块大小与加密时的块大小不同，因为每个块都有自己的IV
        blocks = []
        block_size = self.block_size + 16  # 16字节IV + 4MB数据
        
        i = 0
        while i < len(ciphertext):
            # 查找下一个IV的位置（每4MB+16字节）
            next_i = i + block_size
            if next_i > len(ciphertext):
                next_i = len(ciphertext)
            blocks.append(ciphertext[i:next_i])
            i = next_i
        
        # 使用线程池并行解密
        futures = []
        for block in blocks:
            future = self.executor.submit(self._decrypt_single_block, block, self.sm4_decrypt, key)
            futures.append(future)
        
        # 收集解密结果
        decrypted_blocks = []
        for i, future in enumerate(futures):
            try:
                decrypted_block = future.result()
                decrypted_blocks.append(decrypted_block)
                # 每解密10块打印一次进度
                if (i + 1) % 10 == 0:
                    print(f"    ✓ SM4解密进度: {i + 1}/{len(futures)}")
            except Exception as e:
                raise RuntimeError(f"SM4解密失败: {str(e)}")
        
        # 连接所有解密后的块
        return b''.join(decrypted_blocks)
    
    def _parallel_aes_decrypt(self, ciphertext, key):
        """
        并行解密AES加密的数据
        
        Args:
            ciphertext (bytes): AES加密的数据
            key (bytes): 解密密钥
        
        Returns:
            bytes: 解密后的数据
        """
        # 将AES加密数据分块（每个块包含IV和密文）
        blocks = []
        block_size = self.block_size + 16  # 16字节IV + 4MB数据
        
        i = 0
        while i < len(ciphertext):
            # 查找下一个IV的位置（每4MB+16字节）
            next_i = i + block_size
            if next_i > len(ciphertext):
                next_i = len(ciphertext)
            blocks.append(ciphertext[i:next_i])
            i = next_i
        
        # 使用线程池并行解密
        futures = []
        for block in blocks:
            future = self.executor.submit(self._decrypt_single_block, block, self.aes_decrypt, key)
            futures.append(future)
        
        # 收集解密结果
        decrypted_blocks = []
        for i, future in enumerate(futures):
            try:
                decrypted_block = future.result()
                decrypted_blocks.append(decrypted_block)
                # 每解密10块打印一次进度
                if (i + 1) % 10 == 0:
                    print(f"    ✓ AES解密进度: {i + 1}/{len(futures)}")
            except Exception as e:
                raise RuntimeError(f"AES解密失败: {str(e)}")
        
        # 连接所有解密后的块
        return b''.join(decrypted_blocks)
