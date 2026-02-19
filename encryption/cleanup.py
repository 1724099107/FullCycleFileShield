import os
import shutil
from utils.memory_cleaner import clean_process_memory, clean_virtual_memory
from deletion.bmb21_2019 import BMB212019Deletion

class EncryptionCleanup:
    """
    加密清理模块，用于执行加密后的清理操作
    """
    
    def __init__(self):
        """
        初始化清理模块
        """
        self.deletion_tool = BMB212019Deletion()
    
    def delete_original_folder(self, folder_path):
        """
        使用BMB21-2019标准删除原始文件夹
        
        Args:
            folder_path (str): 原始文件夹路径
        """
        try:
            print(f"开始使用BMB21-2019标准删除原始文件夹: {folder_path}")
            
            # 检查文件夹是否存在
            if not os.path.exists(folder_path):
                print(f"文件夹不存在: {folder_path}")
                return
            
            # 使用BMB21-2019标准删除文件夹
            self.deletion_tool.delete_folder(folder_path)
            
            print(f"✓ 原始文件夹删除完成: {folder_path}")
        except Exception as e:
            raise RuntimeError(f"原始文件夹删除失败: {str(e)}")
    
    def delete_temp_file(self, file_path):
        """
        使用普通方法删除临时文件（优化：避免BMB21-2019标准的复杂删除过程导致文件占用）
        
        Args:
            file_path (str): 临时文件路径
        """
        try:
            print(f"开始删除临时文件: {file_path}")
            
            # 检查文件是否存在
            if not os.path.exists(file_path):
                print(f"临时文件不存在: {file_path}")
                return
            
            # 使用普通方法删除文件，避免BMB21-2019标准的复杂删除过程
            os.remove(file_path)
            
            print(f"✓ 临时文件删除完成: {file_path}")
        except Exception as e:
            # 如果普通删除失败，尝试使用BMB21-2019标准删除
            print(f"普通删除失败，尝试使用BMB21-2019标准删除: {str(e)}")
            try:
                self.deletion_tool.delete_file(file_path)
                print(f"✓ BMB21-2019标准删除完成: {file_path}")
            except Exception as e2:
                raise RuntimeError(f"临时文件删除失败: {str(e2)}")
    
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
    
    def run_cleanup(self, folder_path, temp_file_path):
        """
        执行完整的清理操作
        
        Args:
            folder_path (str): 原始文件夹路径
            temp_file_path (str): 临时文件路径
        """
        try:
            print("开始执行加密后清理操作...")
            
            # 1. 删除临时文件
            self.delete_temp_file(temp_file_path)
            
            # 2. 删除原始文件夹
            self.delete_original_folder(folder_path)
            
            # 3. 清除内存
            self.clear_memory()
            
            print("✓ 所有清理操作完成")
        except Exception as e:
            print(f"清理操作失败: {str(e)}")
            raise
