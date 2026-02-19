import os
import psutil
import tempfile
from pathlib import Path

class EncryptionPreCheck:
    """
    加密前预检，用于检查系统环境和待加密文件夹的完整性
    """
    
    def __init__(self):
        """
        初始化加密前预检
        """
        self.errors = []
        self.warnings = []
    
    def check_tool_integrity(self):
        """
        检查加密工具完整性与合规性
        
        Returns:
            bool: 检查是否通过
        """
        try:
            # 使用依赖检查模块检查必要的模块是否可用
            from utils.dependency_checker import check_dependency
            
            check_dependency("py7zr", extra_info="用于7Z压缩和解压缩")
            check_dependency("hashlib", extra_info="用于哈希计算")
            check_dependency("Cryptodome.Cipher", extra_info="用于加密算法 (pycryptodomex)")
            
            return True
        except ImportError as e:
            self.errors.append(f"加密工具完整性检查失败: {str(e)}")
            return False
    
    def check_disk_space(self, folder_path, required_factor=2):
        """
        检查存储空间是否充足
        
        Args:
            folder_path (str): 待加密文件或文件夹路径
            required_factor (int, optional): 所需空间倍数，默认2倍
        
        Returns:
            bool: 检查是否通过
        """
        try:
            # 计算待加密内容大小
            total_size = 0
            if os.path.isfile(folder_path):
                # 单个文件
                total_size = os.path.getsize(folder_path)
            else:
                # 文件夹
                for path, dirs, files in os.walk(folder_path):
                    for f in files:
                        fp = os.path.join(path, f)
                        total_size += os.path.getsize(fp)
            
            # 获取磁盘可用空间
            if os.path.isfile(folder_path):
                # 对于单个文件，获取文件所在目录的磁盘可用空间
                file_dir = os.path.dirname(folder_path)
                # 如果文件在当前目录，file_dir 会是空字符串，此时使用 '.'
                if not file_dir:
                    file_dir = '.'
                disk_usage = psutil.disk_usage(file_dir)
            else:
                # 对于文件夹，直接获取文件夹所在磁盘的可用空间
                disk_usage = psutil.disk_usage(folder_path)
            available_space = disk_usage.free
            
            # 检查是否有足够的可用空间
            if available_space < total_size * required_factor:
                self.errors.append(f"存储空间不足: 可用空间{available_space}字节，需要{total_size * required_factor}字节")
                return False
            
            return True
        except Exception as e:
            self.errors.append(f"磁盘空间检查失败: {str(e)}")
            return False
    
    def check_file_integrity(self, folder_path):
        """
        扫描文件或文件夹内文件完整性
        
        Args:
            folder_path (str): 待加密文件或文件夹路径
        
        Returns:
            bool: 检查是否通过
        """
        try:
            has_errors = False
            
            if os.path.isfile(folder_path):
                # 单个文件
                fp = folder_path
                
                # 检查文件是否存在
                if not os.path.exists(fp):
                    self.errors.append(f"文件不存在: {fp}")
                    has_errors = True
                else:
                    # 检查文件是否为空
                    if os.path.getsize(fp) == 0:
                        self.warnings.append(f"文件为空: {fp}")
                    
                    # 检查文件是否可读取
                    try:
                        with open(fp, 'rb') as f:
                            f.read(1)
                    except Exception as e:
                        self.errors.append(f"文件无法读取: {fp} - {str(e)}")
                        has_errors = True
            else:
                # 文件夹
                for path, dirs, files in os.walk(folder_path):
                    for f in files:
                        fp = os.path.join(path, f)
                        
                        # 检查文件是否存在
                        if not os.path.exists(fp):
                            self.errors.append(f"文件不存在: {fp}")
                            has_errors = True
                            continue
                        
                        # 检查文件是否为空
                        if os.path.getsize(fp) == 0:
                            self.warnings.append(f"文件为空: {fp}")
                        
                        # 检查文件是否可读取
                        try:
                            with open(fp, 'rb') as f:
                                f.read(1)
                        except Exception as e:
                            self.errors.append(f"文件无法读取: {fp} - {str(e)}")
                            has_errors = True
            
            return not has_errors
        except Exception as e:
            self.errors.append(f"文件完整性检查失败: {str(e)}")
            return False
    
    def check_folder_locked(self, folder_path):
        """
        检查文件或文件夹是否被占用
        
        Args:
            folder_path (str): 待加密文件或文件夹路径
        
        Returns:
            bool: 检查是否通过
        """
        try:
            if os.path.isfile(folder_path):
                # 单个文件 - 检查文件是否可读取
                try:
                    with open(folder_path, 'rb') as f:
                        f.read(1)
                    return True
                except Exception as e:
                    self.errors.append(f"文件被占用或不可读取: {folder_path} - {str(e)}")
                    return False
            else:
                # 文件夹 - 尝试创建临时文件，检查文件夹是否可写入
                temp_file = os.path.join(folder_path, f".tmp_{os.getpid()}")
                with open(temp_file, 'w') as f:
                    f.write("test")
                
                # 删除临时文件
                os.remove(temp_file)
                
                return True
        except Exception as e:
            if os.path.isfile(folder_path):
                self.errors.append(f"文件检查失败: {folder_path} - {str(e)}")
            else:
                self.errors.append(f"文件夹被占用或不可写入: {folder_path} - {str(e)}")
            return False
    
    def run_all_checks(self, folder_path):
        """
        运行所有预检
        
        Args:
            folder_path (str): 待加密文件或文件夹路径
        
        Returns:
            bool: 所有检查是否通过
        """
        # 重置错误和警告列表
        self.errors = []
        self.warnings = []
        
        print("开始加密前预检...")
        
        # 检查1: 工具完整性
        print("  1. 检查加密工具完整性...")
        tool_check = self.check_tool_integrity()
        
        # 检查2: 磁盘空间
        print("  2. 检查存储空间...")
        disk_check = self.check_disk_space(folder_path)
        
        # 检查3: 文件完整性
        print("  3. 检查文件完整性...")
        file_check = self.check_file_integrity(folder_path)
        
        # 检查4: 文件夹是否被占用
        print("  4. 检查文件夹是否被占用...")
        folder_check = self.check_folder_locked(folder_path)
        
        # 输出结果
        print("\n预检结果:")
        if self.warnings:
            print("警告:")
            for warning in self.warnings:
                print(f"  - {warning}")
        
        if self.errors:
            print("错误:")
            for error in self.errors:
                print(f"  - {error}")
        
        # 判断是否通过
        all_passed = tool_check and disk_check and file_check and folder_check
        
        if all_passed:
            print("\n✓ 所有预检通过，可以开始加密")
        else:
            print("\n✗ 预检失败，无法开始加密")
        
        return all_passed
