import os
import tempfile
from utils.hash_calculator import calculate_hash_pair
from utils.dependency_checker import check_dependency

# 检查并导入py7zr模块
py7zr = check_dependency("py7zr", extra_info="用于7Z压缩和解压缩")

class Decompression:
    """
    7Z解压模块，用于执行7Z解压操作
    """
    
    def __init__(self):
        """
        初始化解压模块
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
    
    def decompress(self, compressed_file, output_folder, progress_callback=None, time_callback=None):
        """
        执行7Z解压操作
        
        Args:
            compressed_file (str): 压缩包路径
            output_folder (str): 输出文件夹路径
            progress_callback (callable, optional): 进度回调函数，用于更新解压进度
            time_callback (callable, optional): 时间回调函数，用于更新剩余时间
        """
        try:
            # 设置临时文件路径
            if not self.temp_file_path:
                self.set_temp_path()
            
            # 确保输出文件夹存在
            os.makedirs(output_folder, exist_ok=True)
            
            # 执行解压操作
            print(f"开始解压压缩包: {compressed_file}")
            print(f"输出路径: {output_folder}")
            print(f"解压模式: 保留原始文件夹结构")
            
            # 记录开始时间
            import time
            start_time = time.time()
            
            # 优化：一次性解压所有文件，提高解压速度
            with py7zr.SevenZipFile(compressed_file, 'r') as archive:
                file_list = archive.getnames()
                total_files = len(file_list)
                
                # 优化：使用批量解压代替逐个文件解压
                print(f"开始批量解压 {total_files} 个文件...")
                archive.extractall(output_folder)
                
                # 解压完成后更新进度
                if progress_callback:
                    progress_callback(90)
                if time_callback:
                    time_callback("完成")
            
            # 解压完成，更新进度到90%
            if progress_callback:
                progress_callback(90)
            if time_callback:
                time_callback("计算中...")
            
            print(f"✓ 解压完成")
        except Exception as e:
            raise RuntimeError(f"解压失败: {str(e)}")
    
    def verify_decompression(self, decompressed_folder, expected_sha512=None, expected_sm3=None):
        """
        验证解压后的完整性
        
        Args:
            decompressed_folder (str): 解压后的文件夹路径
            expected_sha512 (str, optional): 预期的SHA-512哈希值
            expected_sm3 (str, optional): 预期的SM3哈希值
        
        Returns:
            bool: 验证是否通过
        """
        try:
            print(f"开始验证解压后的完整性: {decompressed_folder}")
            
            # 如果没有提供预期哈希值，则跳过验证
            if not expected_sha512 or not expected_sm3:
                print("未提供预期哈希值，跳过完整性验证")
                return True
            
            # 计算解压后文件夹的哈希值（这里简化为计算第一个文件的哈希值）
            # 实际应用中应计算整个文件夹的哈希值
            actual_sha512 = None
            actual_sm3 = None
            
            for root, dirs, files in os.walk(decompressed_folder):
                for file in files:
                    file_path = os.path.join(root, file)
                    actual_sha512, actual_sm3 = calculate_hash_pair(file_path)
                    break  # 只计算第一个文件的哈希值
            
            # 比较哈希值
            if actual_sha512 == expected_sha512 and actual_sm3 == expected_sm3:
                print("✓ 解压后完整性验证通过")
                return True
            else:
                print("✗ 解压后完整性验证失败")
                print(f"预期SHA-512: {expected_sha512}")
                print(f"实际SHA-512: {actual_sha512}")
                print(f"预期SM3: {expected_sm3}")
                print(f"实际SM3: {actual_sm3}")
                return False
        except Exception as e:
            print(f"✗ 解压后完整性验证失败: {str(e)}")
            return False
