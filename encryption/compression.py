import os
import tempfile
from utils.hash_calculator import calculate_hash_pair
from utils.dependency_checker import check_dependency

# 检查并导入py7zr模块
py7zr = check_dependency("py7zr", extra_info="用于7Z压缩和解压缩")

class Compression:
    """
    7Z压缩模块，用于执行7Z压缩操作
    """
    
    def __init__(self):
        """
        初始化压缩模块
        """
        self.temp_file_path = None
    
    def set_temp_path(self, temp_path=None):
        """
        设置临时文件路径
        
        Args:
            temp_path (str, optional): 临时文件路径，默认使用系统内存虚拟盘
        """
        if temp_path:
            self.temp_file_path = temp_path
        else:
            # 使用系统默认的临时目录
            self.temp_file_path = tempfile.gettempdir()
    
    def compress(self, input_path, output_file=None, progress_callback=None, time_callback=None):
        """
        执行7Z压缩操作，支持单个文件、多个文件或文件夹
        
        Args:
            input_path (str or list): 待压缩的文件路径、文件路径列表或文件夹路径
            output_file (str, optional): 输出压缩包路径，默认在临时目录生成
            progress_callback (callable, optional): 进度回调函数，用于更新压缩进度
            time_callback (callable, optional): 时间回调函数，用于更新剩余时间
        
        Returns:
            tuple: (压缩包路径, sha512_hash, sm3_hash)
        """
        try:
            # 设置临时文件路径
            if not self.temp_file_path:
                self.set_temp_path()
            
            # 生成输出文件路径
            if not output_file:
                # 生成唯一的临时文件名
                import uuid
                unique_name = f'Temp_File_{uuid.uuid4().hex[:8]}.7z'
                output_file = os.path.join(self.temp_file_path, unique_name)
            
            # 执行压缩操作
            try:
                # 记录开始时间
                import time
                start_time = time.time()
                
                # 计算总文件数（优化：使用更高效的方式）
                total_files = 0
                if isinstance(input_path, list):
                    # 快速计算列表中的文件数
                    total_files = sum(1 for path in input_path if os.path.isfile(path))
                elif os.path.isdir(input_path):
                    # 计算文件夹中的文件数（优化：使用生成器表达式）
                    total_files = sum(len(files) for _, _, files in os.walk(input_path))
                elif os.path.isfile(input_path):
                    total_files = 1
                
                processed_files = 0
                
                # 使用快速压缩配置
                with py7zr.SevenZipFile(output_file, 'w', filters=[{'id': py7zr.FILTER_LZMA2, 'preset': 1}]) as archive:
                    
                    if isinstance(input_path, list):
                        # 处理多个文件
                        print(f"开始压缩 {len(input_path)} 个文件")
                        for file_path in input_path:
                            if os.path.isfile(file_path):
                                # 添加单个文件，保留相对路径结构
                                archive.write(file_path, os.path.basename(file_path))
                                processed_files += 1
                            elif os.path.isdir(file_path):
                                # 添加文件夹
                                archive.writeall(file_path, os.path.basename(file_path))
                                # 计算文件夹中的文件数
                                for root, dirs, files in os.walk(file_path):
                                    processed_files += len(files)
                            
                            # 更新进度
                            if progress_callback and total_files > 0:
                                progress = min(20, int((processed_files / total_files) * 20))
                                progress_callback(progress)
                            
                            # 更新时间
                            if time_callback:
                                elapsed_time = time.time() - start_time
                                if processed_files > 0:
                                    estimated_total_time = (elapsed_time / processed_files) * total_files
                                    remaining_time = max(0, estimated_total_time - elapsed_time)
                                    time_callback(f"{int(remaining_time)}秒")
                    elif os.path.isdir(input_path):
                        # 处理单个文件夹
                        print(f"开始压缩文件夹: {input_path}")
                        
                        # 遍历文件夹，逐个添加文件并更新进度
                        for root, dirs, files in os.walk(input_path):
                            for file in files:
                                file_path = os.path.join(root, file)
                                arcname = os.path.relpath(file_path, input_path)
                                archive.write(file_path, arcname)
                                processed_files += 1
                                
                                # 更新进度
                                if progress_callback and total_files > 0:
                                    progress = min(20, int((processed_files / total_files) * 20))
                                    progress_callback(progress)
                                
                                # 更新时间
                                if time_callback:
                                    elapsed_time = time.time() - start_time
                                    if processed_files > 0:
                                        estimated_total_time = (elapsed_time / processed_files) * total_files
                                        remaining_time = max(0, estimated_total_time - elapsed_time)
                                        time_callback(f"{int(remaining_time)}秒")
                    elif os.path.isfile(input_path):
                        # 处理单个文件
                        print(f"开始压缩文件: {input_path}")
                        archive.write(input_path, os.path.basename(input_path))
                        processed_files = 1
                        
                        # 更新进度
                        if progress_callback:
                            progress_callback(10)
                        
                        # 更新时间
                        if time_callback:
                            elapsed_time = time.time() - start_time
                            estimated_total_time = elapsed_time * 2  # 假设还需要同样的时间
                            remaining_time = max(0, estimated_total_time - elapsed_time)
                            time_callback(f"{int(remaining_time)}秒")
                    else:
                        raise RuntimeError(f"无效的输入路径: {input_path}")
                
                # 压缩完成，更新进度到25%
                if progress_callback:
                    progress_callback(25)
                if time_callback:
                    time_callback("计算中...")
            except Exception as e:
                # 清理可能创建的部分文件
                if os.path.exists(output_file):
                    os.remove(output_file)
                raise RuntimeError(f"压缩失败: {str(e)}")
            
            print(f"✓ 压缩完成: {output_file}")
            
            # 计算压缩包的双哈希值
            print("开始计算压缩包哈希值...")
            sha512_hash, sm3_hash = calculate_hash_pair(output_file)
            print(f"✓ SHA-512哈希值: {sha512_hash}")
            print(f"✓ SM3哈希值: {sm3_hash}")
            
            return (output_file, sha512_hash, sm3_hash)
        except Exception as e:
            # 清理临时文件
            if output_file and os.path.exists(output_file):
                os.remove(output_file)
            raise RuntimeError(f"压缩失败: {str(e)}")
    
    def decompress(self, compressed_file, output_folder):
        """
        执行7Z解压操作
        
        Args:
            compressed_file (str): 压缩包路径
            output_folder (str): 输出文件夹路径
        """
        try:
            print(f"开始解压压缩包: {compressed_file}")
            print(f"输出路径: {output_folder}")
            
            with py7zr.SevenZipFile(compressed_file, 'r') as archive:
                archive.extractall(output_folder)
            
            print(f"✓ 解压完成")
        except Exception as e:
            raise RuntimeError(f"解压失败: {str(e)}")
    
    def verify_compression(self, compressed_file, expected_sha512, expected_sm3):
        """
        验证压缩包完整性
        
        Args:
            compressed_file (str): 压缩包路径
            expected_sha512 (str): 预期的SHA-512哈希值
            expected_sm3 (str): 预期的SM3哈希值
        
        Returns:
            bool: 验证是否通过
        """
        try:
            print(f"开始验证压缩包完整性: {compressed_file}")
            
            # 计算实际哈希值
            actual_sha512, actual_sm3 = calculate_hash_pair(compressed_file)
            
            # 比较哈希值
            if actual_sha512 == expected_sha512 and actual_sm3 == expected_sm3:
                print("✓ 压缩包完整性验证通过")
                return True
            else:
                print("✗ 压缩包完整性验证失败")
                print(f"预期SHA-512: {expected_sha512}")
                print(f"实际SHA-512: {actual_sha512}")
                print(f"预期SM3: {expected_sm3}")
                print(f"实际SM3: {actual_sm3}")
                return False
        except Exception as e:
            print(f"✗ 压缩包完整性验证失败: {str(e)}")
            return False
