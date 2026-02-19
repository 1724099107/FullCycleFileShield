import os
import shutil
from utils.memory_cleaner import clean_process_memory, clean_virtual_memory
from deletion.bmb21_2019 import BMB212019Deletion

class DecryptionCleanup:
    """
    解密清理模块，用于执行解密后的清理操作
    """
    
    def __init__(self):
        """
        初始化解密清理模块
        """
        self.deletion_tool = BMB212019Deletion()
    
    def delete_temp_file(self, file_path):
        """
        使用BMB21-2019标准删除临时文件
        
        Args:
            file_path (str): 临时文件路径
        """
        try:
            print(f"开始使用BMB21-2019标准删除临时文件: {file_path}")
            
            # 检查文件是否存在
            if not os.path.exists(file_path):
                print(f"临时文件不存在: {file_path}")
                return
            
            # 使用BMB21-2019标准删除文件
            self.deletion_tool.delete_file(file_path)
            
            print(f"✓ 临时文件删除完成: {file_path}")
        except Exception as e:
            raise RuntimeError(f"临时文件删除失败: {str(e)}")
    
    def delete_encrypted_file(self, encrypted_file):
        """
        使用BMB21-2019标准删除加密产物
        
        Args:
            encrypted_file (str): 加密产物路径
        """
        try:
            print(f"开始使用BMB21-2019标准删除加密产物: {encrypted_file}")
            
            # 检查文件是否存在
            if not os.path.exists(encrypted_file):
                print(f"加密产物不存在: {encrypted_file}")
                return
            
            # 使用BMB21-2019标准删除文件
            self.deletion_tool.delete_file(encrypted_file)
            
            print(f"✓ 加密产物删除完成: {encrypted_file}")
        except Exception as e:
            raise RuntimeError(f"加密产物删除失败: {str(e)}")
    
    def clear_memory(self):
        """
        清除内存中的敏感信息
        """
        try:
            print("开始清除进程内存...")
            clean_process_memory()
            print("✓ 进程内存清除完成")
            
            print("开始清除虚拟内存...")
            clean_virtual_memory()
            print("✓ 虚拟内存清除完成")
        except Exception as e:
            raise RuntimeError(f"内存清理失败: {str(e)}")
    
    def run_cleanup(self, temp_file_path, encrypted_file=None, delete_encrypted=False):
        """
        执行完整的解密后清理操作
        
        Args:
            temp_file_path (str): 临时文件路径
            encrypted_file (str, optional): 加密产物路径
            delete_encrypted (bool, optional): 是否删除加密产物，默认不删除
        """
        try:
            print("开始执行解密后清理操作...")
            
            # 1. 删除临时文件
            self.delete_temp_file(temp_file_path)
            
            # 2. 可选地删除加密产物
            if delete_encrypted and encrypted_file:
                self.delete_encrypted_file(encrypted_file)
            
            # 3. 清除内存
            self.clear_memory()
            
            print("✓ 所有清理操作完成")
        except Exception as e:
            print(f"清理操作失败: {str(e)}")
            raise
