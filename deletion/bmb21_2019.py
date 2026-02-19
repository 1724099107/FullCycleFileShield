import os
import sys
import platform
import subprocess
import time
import threading
from concurrent.futures import ThreadPoolExecutor
from utils.memory_cleaner import clear_memory

class BMB212019Deletion:
    """
    基于BMB21-2019标准的文件彻底删除工具
    """
    
    def __init__(self):
        """
        初始化BMB21-2019删除工具
        """
        self.overwrite_patterns = [
            b'\x00',  # 第一遍：全零
            b'\xFF',  # 第二遍：全1
            None,     # 第三遍：随机字节
            b'\x55',  # 第四遍：交替01
            None      # 第五遍：随机字节
        ]
        self.block_size = 1048576  # 优化：增大块大小到1MB，显著提高I/O效率
        self.max_threads = 4  # 优化：添加并行处理支持，使用4个线程
    
    def is_file_locked(self, file_path):
        """
        检查文件是否被占用
        
        Args:
            file_path (str): 文件路径
        
        Returns:
            bool: 文件是否被占用
        """
        try:
            if os.path.exists(file_path):
                with open(file_path, 'a+b') as f:
                    f.flush()
            return False
        except Exception:
            return True
    
    def wait_for_file_unlock(self, file_path, timeout=30):
        """
        等待文件解锁
        
        Args:
            file_path (str): 文件路径
            timeout (int, optional): 超时时间（秒），默认30秒
        
        Returns:
            bool: 文件是否成功解锁
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            if not self.is_file_locked(file_path):
                return True
            time.sleep(0.5)
        return False
    
    def overwrite_file(self, file_path):
        """
        按照BMB21-2019标准对文件进行多次覆写
        
        Args:
            file_path (str): 文件路径
        """
        try:
            # 获取文件大小
            file_size = os.path.getsize(file_path)
            
            # 如果文件为空，跳过覆写
            if file_size == 0:
                return
            
            # 预先生成所有模式，避免重复计算
            patterns = []
            for pattern in self.overwrite_patterns:
                if pattern is None:
                    # 生成随机字节序列
                    patterns.append(os.urandom(self.block_size))
                else:
                    # 确保pattern长度为block_size
                    if len(pattern) < self.block_size:
                        # 先计算乘法，再切片，修复运算符优先级问题
                        patterns.append((pattern * (self.block_size // len(pattern) + 1))[:self.block_size])
                    else:
                        patterns.append(pattern[:self.block_size])
            
            # 计算需要多少个完整块和剩余字节
            full_blocks = file_size // self.block_size
            remaining_bytes = file_size % self.block_size
            
            # 定义每个线程处理的块数
            blocks_per_thread = max(1, full_blocks // self.max_threads)
            
            # 执行5遍覆写
            for i, pattern in enumerate(patterns):
                print(f"  执行第 {i + 1} 遍覆写...")
                
                # 定义线程函数
                def overwrite_worker(start_block, end_block, worker_pattern):
                    with open(file_path, 'rb+', buffering=0) as f:
                        for block_idx in range(start_block, end_block):
                            # 计算块的起始位置
                            offset = block_idx * self.block_size
                            f.seek(offset)
                            f.write(worker_pattern)
                            
                            # 每处理10个块打印一次进度
                            if (block_idx - start_block + 1) % 10 == 0:
                                print(f"    线程进度: {block_idx - start_block + 1}/{end_block - start_block}")
                
                # 使用线程池管理线程
                with ThreadPoolExecutor(max_workers=self.max_threads, thread_name_prefix="Overwrite-Worker") as executor:
                    futures = []
                    for thread_idx in range(self.max_threads):
                        start_block = thread_idx * blocks_per_thread
                        end_block = min(start_block + blocks_per_thread, full_blocks)
                        
                        if start_block < end_block:
                            future = executor.submit(overwrite_worker, start_block, end_block, pattern)
                            futures.append(future)
                    
                    # 等待所有任务完成
                    for future in futures:
                        future.result()
                
                # 处理剩余字节
                if remaining_bytes > 0:
                    with open(file_path, 'rb+', buffering=0) as f:
                        f.seek(full_blocks * self.block_size)
                        f.write(pattern[:remaining_bytes])
                
                # 刷新到磁盘
                with open(file_path, 'rb+', buffering=0) as f:
                    f.flush()
                    os.fsync(f.fileno())
                
                print(f"  第 {i + 1} 遍覆写完成")
        except Exception as e:
            raise RuntimeError(f"文件覆写失败: {str(e)}")
    
    def erase_metadata(self, file_path):
        """
        擦除文件元数据
        
        Args:
            file_path (str): 文件路径
        """
        return self.delete_file_metadata(file_path)
    
    def delete_file_metadata(self, file_path):
        """
        删除文件元数据
        
        Args:
            file_path (str): 文件路径
        """
        try:
            # 仅在文件存在时执行
            if not os.path.exists(file_path):
                return
            
            # 修改文件的创建时间、修改时间和访问时间
            if platform.system() == 'Windows':
                # Windows系统
                import win32file
                import win32con
                import pywintypes
                
                # 设置文件时间为1970-01-01 00:00:00
                # 使用更兼容的时间格式
                import datetime
                new_time = pywintypes.Time(datetime.datetime(1970, 1, 1, 0, 0, 0))
                win32file.SetFileTime(
                    win32file.CreateFile(
                        file_path,
                        win32con.GENERIC_WRITE,
                        win32con.FILE_SHARE_WRITE | win32con.FILE_SHARE_READ,
                        None,
                        win32con.OPEN_EXISTING,
                        0,
                        None
                    ),
                    new_time,  # 创建时间
                    new_time,  # 访问时间
                    new_time   # 修改时间
                )
            else:
                # Linux/macOS系统
                subprocess.run(['touch', '-t', '197001010000.00', file_path], check=True)
                
            # 重命名文件为随机名称
            dir_path = os.path.dirname(file_path)
            random_name = os.urandom(16).hex()
            new_file_path = os.path.join(dir_path, random_name)
            os.rename(file_path, new_file_path)
            
            return new_file_path
        except Exception as e:
            print(f"警告: 文件元数据删除失败: {str(e)}")
            return file_path
    
    def low_level_format(self, device_path):
        """
        对磁盘设备执行低级格式化（仅对机械硬盘有效）
        
        Args:
            device_path (str): 磁盘设备路径
        """
        try:
            if platform.system() == 'Windows':
                # Windows系统：使用diskpart命令
                subprocess.run([
                    'diskpart', '/s', 'format_script.txt'
                ], check=True, input=f"select disk {device_path}\nclean\ncreate partition primary\nformat quick\n")
            elif platform.system() == 'Linux':
                # Linux系统：使用dd命令
                subprocess.run([
                    'dd', f'if=/dev/zero', f'of={device_path}', 'bs=4096', 'status=progress'
                ], check=True)
            elif platform.system() == 'Darwin':
                # macOS系统：使用diskutil命令
                subprocess.run([
                    'diskutil', 'zeroDisk', device_path
                ], check=True)
        except Exception as e:
            print(f"警告: 低级格式化失败: {str(e)}")
    
    def trim_ssd(self, device_path):
        """
        对固态硬盘执行TRIM操作
        
        Args:
            device_path (str): 磁盘设备路径
        """
        try:
            if platform.system() == 'Windows':
                # Windows系统：使用Optimize-Volume命令
                subprocess.run([
                    'powershell', '-Command', f'Optimize-Volume -DriveLetter {device_path} -ReTrim -Verbose'
                ], check=True)
            elif platform.system() == 'Linux':
                # Linux系统：使用fstrim命令
                subprocess.run([
                    'fstrim', '--verbose', device_path
                ], check=True)
            elif platform.system() == 'Darwin':
                # macOS系统：使用trimforce命令
                subprocess.run([
                    'diskutil', 'trimforce', 'enable', device_path
                ], check=True)
        except Exception as e:
            print(f"警告: SSD TRIM操作失败: {str(e)}")
    
    def clear_memory_cache(self, file_path):
        """
        清除与文件相关的内存缓存
        
        Args:
            file_path (str): 文件路径
        """
        try:
            if platform.system() == 'Linux':
                # Linux系统：清除文件缓存
                subprocess.run([
                    'sync', f'echo 3 > /proc/sys/vm/drop_caches'
                ], check=True, shell=True)
            elif platform.system() == 'Darwin':
                # macOS系统：执行purge命令
                subprocess.run(['purge'], check=True)
            elif platform.system() == 'Windows':
                # Windows系统：清除内存缓存
                subprocess.run(['wmic', 'computersystem', 'set', 'AutomaticManagedPagefile=True'], check=True)
        except Exception as e:
            print(f"警告: 内存缓存清除失败: {str(e)}")
    
    def delete_file(self, file_path, max_retries=3, skip_trim=False):
        """
        按照BMB21-2019标准彻底删除文件，支持失败重试
        
        Args:
            file_path (str): 文件路径
            max_retries (int, optional): 最大重试次数，默认3次
            skip_trim (bool, optional): 是否跳过SSD TRIM操作，默认False
        """
        for retry in range(max_retries):
            try:
                # 检查文件是否存在
                if not os.path.exists(file_path):
                    return
                
                # 检查文件是否被占用
                if self.is_file_locked(file_path):
                    if not self.wait_for_file_unlock(file_path, timeout=5):  # 优化：缩短等待时间到5秒
                        raise RuntimeError(f"文件无法解锁: {file_path}")
                
                # 1. 文件数据多次覆写
                self.overwrite_file(file_path)
                
                # 2. 元数据彻底擦除
                new_file_path = self.delete_file_metadata(file_path)
                
                # 3. 删除文件
                os.remove(new_file_path)
                
                return
            except Exception as e:
                if retry < max_retries - 1:
                    time.sleep(0.5)  # 优化：缩短重试间隔到0.5秒
                else:
                    raise RuntimeError(f"文件删除失败（已重试{max_retries}次）: {str(e)}")
    
    def delete_files(self, file_paths, max_retries=3):
        """
        批量删除多个文件（非文件夹），支持并行处理
        
        Args:
            file_paths (list): 文件路径列表
            max_retries (int, optional): 最大重试次数，默认3次
        
        Returns:
            tuple: (成功删除的文件数, 失败的文件数, 失败的文件列表)
        """
        # 过滤掉不存在的文件，减少不必要的处理
        existing_files = [f for f in file_paths if os.path.exists(f)]
        total_files = len(existing_files)
        
        success_count = 0
        failure_count = 0
        failed_files = []
        
        # 使用线程锁保护共享计数器
        lock = threading.Lock()
        
        def delete_single_file(file_path):
            nonlocal success_count, failure_count, failed_files
            try:
                self.delete_file(file_path, max_retries=max_retries, skip_trim=True)
                with lock:
                    success_count += 1
            except Exception as e:
                with lock:
                    failure_count += 1
                    failed_files.append((file_path, str(e)))
        
        # 使用ThreadPoolExecutor管理线程
        with ThreadPoolExecutor(max_workers=self.max_threads, thread_name_prefix="Delete-Worker") as executor:
            # 提交所有删除任务
            futures = [executor.submit(delete_single_file, file_path) for file_path in existing_files]
            
            # 等待所有任务完成
            for future in futures:
                future.result()
        
        # 优化：只在有文件被删除时清除内存缓存
        if success_count > 0:
            # 使用第一个成功删除的文件路径调用，或者使用空字符串
            if existing_files:
                self.clear_memory_cache(existing_files[0])
            else:
                self.clear_memory_cache('')
        
        return success_count, failure_count, failed_files
    
    def delete_folder(self, folder_path):
        """
        按照BMB21-2019标准彻底删除文件夹
        
        Args:
            folder_path (str): 文件夹路径
        """
        try:
            print(f"开始删除文件夹: {folder_path}")
            
            # 检查文件夹是否存在
            if not os.path.exists(folder_path):
                print(f"文件夹不存在: {folder_path}")
                return
            
            # 收集所有文件路径
            all_files = []
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    all_files.append(file_path)
            
            print(f"✓ 收集到 {len(all_files)} 个文件")
            
            # 使用多线程删除文件
            if all_files:
                success_count, failure_count, failed_files = self.delete_files(all_files)
                print(f"✓ 文件删除完成: 成功 {success_count} 个，失败 {failure_count} 个")
                
                if failed_files:
                    print("\n失败的文件:")
                    for file_path, error in failed_files[:5]:  # 只显示前5个失败的文件
                        print(f"  - {file_path}: {error}")
                    if len(failed_files) > 5:
                        print(f"  ... 还有 {len(failed_files) - 5} 个失败文件")
            
            # 遍历删除子文件夹
            print("开始删除子文件夹...")
            for root, dirs, files in os.walk(folder_path, topdown=False):
                for dir in dirs:
                    dir_path = os.path.join(root, dir)
                    try:
                        os.rmdir(dir_path)
                        print(f"✓ 子文件夹删除完成: {dir_path}")
                    except Exception as e:
                        print(f"警告: 子文件夹删除失败: {str(e)}")
            
            # 删除主文件夹
            os.rmdir(folder_path)
            print(f"✓ 文件夹彻底删除完成: {folder_path}")
        except Exception as e:
            raise RuntimeError(f"文件夹删除失败: {str(e)}")
    
    def _is_ssd(self, file_path):
        """
        判断文件所在的磁盘是否为SSD
        
        Args:
            file_path (str): 文件路径
        
        Returns:
            bool: 是否为SSD
        """
        try:
            if platform.system() == 'Windows':
                # Windows系统：使用wmic命令
                device_path = self._get_device_path(file_path)
                result = subprocess.run([
                    'wmic', 'diskdrive', 'where', f'deviceid="{device_path}"', 'get', 'mediatype'
                ], capture_output=True, text=True, check=True)
                return 'SSD' in result.stdout or 'Solid State' in result.stdout
            elif platform.system() == 'Linux':
                # Linux系统：检查/sys/block/设备/queue/rotational文件
                device_path = self._get_device_path(file_path)
                rotational_file = f'/sys/block/{device_path}/queue/rotational'
                if os.path.exists(rotational_file):
                    with open(rotational_file, 'r') as f:
                        return f.read().strip() == '0'
            elif platform.system() == 'Darwin':
                # macOS系统：使用diskutil命令
                result = subprocess.run([
                    'diskutil', 'info', file_path
                ], capture_output=True, text=True, check=True)
                return 'Solid State' in result.stdout
            return False
        except Exception:
            return False
    
    def _get_device_path(self, file_path):
        """
        获取文件所在的磁盘设备路径
        
        Args:
            file_path (str): 文件路径
        
        Returns:
            str: 磁盘设备路径
        """
        try:
            if platform.system() == 'Windows':
                # Windows系统：返回驱动器号
                drive = os.path.splitdrive(file_path)[0]
                return drive
            elif platform.system() == 'Linux':
                # Linux系统：使用df命令获取设备路径
                result = subprocess.run([
                    'df', '--output=source', file_path
                ], capture_output=True, text=True, check=True)
                return result.stdout.strip().split('\n')[1]
            elif platform.system() == 'Darwin':
                # macOS系统：使用df命令获取设备路径
                result = subprocess.run([
                    'df', '-h', file_path
                ], capture_output=True, text=True, check=True)
                return result.stdout.strip().split('\n')[1].split()[0]
            return ''
        except Exception:
            return ''
    
    def verify_deletion(self, original_path):
        """
        验证文件/文件夹是否已彻底删除
        
        Args:
            original_path (str): 原始文件/文件夹路径
        
        Returns:
            bool: 删除是否成功
        """
        try:
            # 检查文件/文件夹是否存在
            if os.path.exists(original_path):
                return False
            
            # 对于文件，尝试使用数据恢复工具扫描（这里简化为返回True）
            # 实际应用中应使用专业的数据恢复工具进行验证
            return True
        except Exception:
            return False
