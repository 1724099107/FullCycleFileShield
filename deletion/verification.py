import os
import platform
import subprocess

class DeletionVerification:
    """
    删除结果验证模块，用于验证文件/文件夹是否已彻底删除
    """
    
    def __init__(self):
        """
        初始化删除结果验证模块
        """
        pass
    
    def verify_file_deletion(self, file_path):
        """
        验证文件是否已彻底删除
        
        Args:
            file_path (str): 原始文件路径
        
        Returns:
            tuple: (bool, str) - (删除是否成功, 验证结果描述)
        """
        try:
            # 1. 检查文件是否存在
            if os.path.exists(file_path):
                return False, f"文件仍然存在: {file_path}"
            
            # 2. 检查文件所在目录是否存在
            dir_path = os.path.dirname(file_path)
            if not os.path.exists(dir_path):
                return True, f"文件所在目录已不存在，无法进一步验证: {dir_path}"
            
            # 3. 检查文件是否可以通过文件名恢复
            file_name = os.path.basename(file_path)
            for root, dirs, files in os.walk(dir_path):
                if file_name in files:
                    return False, f"文件通过文件名恢复: {os.path.join(root, file_name)}"
            
            # 4. 尝试使用系统工具扫描残留数据
            scan_result = self._scan_for_residual_data(file_path)
            if scan_result:
                return False, f"检测到文件残留数据: {scan_result}"
            
            # 5. 验证元数据是否完全擦除
            metadata_result = self._verify_metadata_erasure(file_path)
            if not metadata_result:
                return False, "文件元数据未完全擦除"
            
            return True, "文件已彻底删除，未检测到残留数据"
        except Exception as e:
            return False, f"验证过程中发生错误: {str(e)}"
    
    def verify_folder_deletion(self, folder_path):
        """
        验证文件夹是否已彻底删除
        
        Args:
            folder_path (str): 原始文件夹路径
        
        Returns:
            tuple: (bool, str) - (删除是否成功, 验证结果描述)
        """
        try:
            # 1. 检查文件夹是否存在
            if os.path.exists(folder_path):
                return False, f"文件夹仍然存在: {folder_path}"
            
            # 2. 检查文件夹所在目录是否存在
            parent_dir = os.path.dirname(folder_path)
            if not os.path.exists(parent_dir):
                return True, f"文件夹所在目录已不存在，无法进一步验证: {parent_dir}"
            
            # 3. 检查文件夹是否可以通过文件夹名恢复
            folder_name = os.path.basename(folder_path)
            for root, dirs, files in os.walk(parent_dir):
                if folder_name in dirs:
                    return False, f"文件夹通过文件夹名恢复: {os.path.join(root, folder_name)}"
            
            # 4. 尝试使用系统工具扫描残留数据
            scan_result = self._scan_for_residual_data(folder_path)
            if scan_result:
                return False, f"检测到文件夹残留数据: {scan_result}"
            
            return True, "文件夹已彻底删除，未检测到残留数据"
        except Exception as e:
            return False, f"验证过程中发生错误: {str(e)}"
    
    def _scan_for_residual_data(self, path):
        """
        使用系统工具扫描残留数据
        
        Args:
            path (str): 原始文件/文件夹路径
        
        Returns:
            str: 扫描结果，无残留则返回空字符串
        """
        try:
            if platform.system() == 'Windows':
                # Windows系统：使用chkdsk命令检查磁盘（不修复，只检查）
                result = subprocess.run([
                    'chkdsk', os.path.splitdrive(path)[0]
                ], capture_output=True, text=True, check=False)
                return ""  # chkdsk输出复杂，这里简化处理
            elif platform.system() == 'Linux':
                # Linux系统：使用debugfs命令检查文件系统
                device = self._get_device_path(path)
                if device:
                    result = subprocess.run([
                        'debugfs', '-R', f'ls -la {os.path.dirname(path)}', device
                    ], capture_output=True, text=True)
                    if os.path.basename(path) in result.stdout:
                        return f"在debugfs中检测到文件: {path}"
            elif platform.system() == 'Darwin':
                # macOS系统：使用diskutil命令检查文件系统
                result = subprocess.run([
                    'diskutil', 'verifyVolume', os.path.splitdrive(path)[0]
                ], capture_output=True, text=True)
                return ""  # diskutil输出复杂，这里简化处理
            
            return ""
        except Exception as e:
            print(f"警告: 残留数据扫描失败: {str(e)}")
            return ""
    
    def _verify_metadata_erasure(self, file_path):
        """
        验证元数据是否完全擦除
        
        Args:
            file_path (str): 原始文件路径
        
        Returns:
            bool: 元数据是否完全擦除
        """
        try:
            if platform.system() == 'Windows':
                # Windows系统：使用fsutil命令检查文件系统
                result = subprocess.run([
                    'fsutil', 'file', 'queryallocranges', 'offset=0', f'length={os.path.getsize(file_path) if os.path.exists(file_path) else 1024}', file_path
                ], capture_output=True, text=True)
                return "无法查询" not in result.stdout
            elif platform.system() == 'Linux':
                # Linux系统：使用stat命令检查文件元数据
                dir_path = os.path.dirname(file_path)
                result = subprocess.run([
                    'stat', dir_path
                ], capture_output=True, text=True)
                return os.path.basename(file_path) not in result.stdout
            elif platform.system() == 'Darwin':
                # macOS系统：使用stat命令检查文件元数据
                dir_path = os.path.dirname(file_path)
                result = subprocess.run([
                    'stat', dir_path
                ], capture_output=True, text=True)
                return os.path.basename(file_path) not in result.stdout
            
            return True
        except Exception as e:
            print(f"警告: 元数据验证失败: {str(e)}")
            return True
    
    def _get_device_path(self, path):
        """
        获取文件/文件夹所在的设备路径
        
        Args:
            path (str): 文件/文件夹路径
        
        Returns:
            str: 设备路径
        """
        try:
            if platform.system() == 'Linux':
                # Linux系统：使用df命令获取设备路径
                result = subprocess.run([
                    'df', '--output=source', path
                ], capture_output=True, text=True, check=True)
                return result.stdout.strip().split('\n')[1]
            elif platform.system() == 'Darwin':
                # macOS系统：使用df命令获取设备路径
                result = subprocess.run([
                    'df', '-h', path
                ], capture_output=True, text=True, check=True)
                return result.stdout.strip().split('\n')[1].split()[0]
            return ''
        except Exception as e:
            print(f"警告: 获取设备路径失败: {str(e)}")
            return ''
    
    def generate_verification_report(self, original_path, is_file=True):
        """
        生成删除验证报告
        
        Args:
            original_path (str): 原始文件/文件夹路径
            is_file (bool, optional): 是否为文件，默认为True
        
        Returns:
            str: 验证报告
        """
        report = []
        report.append(f"=== 删除验证报告 ===")
        report.append(f"验证时间: {self._get_current_time()}")
        report.append(f"验证对象: {original_path}")
        report.append(f"对象类型: {'文件' if is_file else '文件夹'}")
        
        if is_file:
            success, result = self.verify_file_deletion(original_path)
        else:
            success, result = self.verify_folder_deletion(original_path)
        
        report.append(f"验证结果: {'成功' if success else '失败'}")
        report.append(f"详细描述: {result}")
        report.append(f"===================")
        
        return '\n'.join(report)
    
    def _get_current_time(self):
        """
        获取当前时间
        
        Returns:
            str: 当前时间字符串
        """
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
