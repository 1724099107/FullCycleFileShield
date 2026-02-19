import os
import json
from utils.hash_calculator import calculate_hash

class DecryptionPreCheck:
    """
    解密前预检，用于检查系统环境和加密产物的完整性
    """
    
    def __init__(self):
        """
        初始化解密前预检
        """
        self.errors = []
        self.warnings = []
    
    def check_tool_integrity(self):
        """
        检查解密工具完整性与合规性
        
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
            self.errors.append(f"解密工具完整性检查失败: {str(e)}")
            return False
    
    def check_encrypted_file(self, encrypted_file):
        """
        检查加密产物完整性
        
        Args:
            encrypted_file (str): 加密产物路径
        
        Returns:
            bool: 检查是否通过
        """
        try:
            # 检查文件是否存在
            if not os.path.exists(encrypted_file):
                self.errors.append(f"加密产物不存在: {encrypted_file}")
                return False
            
            # 检查文件是否可读取
            try:
                with open(encrypted_file, 'r') as f:
                    encrypted_data = json.load(f)
                
                # 检查加密产物是否包含必要字段
                required_fields = ['c3', 'qkc', 'signature', 'sha512', 'sm3']
                for field in required_fields:
                    if field not in encrypted_data:
                        self.errors.append(f"加密产物缺少必要字段: {field}")
                        return False
                
                return True
            except json.JSONDecodeError:
                self.errors.append(f"加密产物格式错误: {encrypted_file}")
                return False
            except Exception as e:
                self.errors.append(f"加密产物读取失败: {str(e)}")
                return False
        except Exception as e:
            self.errors.append(f"加密产物检查失败: {str(e)}")
            return False
    
    def verify_encrypted_file_integrity(self, encrypted_file, master_key):
        """
        验证加密产物完整性
        
        Args:
            encrypted_file (str): 加密产物路径
            master_key (bytes): 主密钥
        
        Returns:
            bool: 检查是否通过
        """
        try:
            # 读取加密产物内容
            with open(encrypted_file, 'r') as f:
                encrypted_data = json.load(f)
            
            # 解析加密产物数据
            import base64
            c3 = base64.b64decode(encrypted_data['c3'])
            signature = base64.b64decode(encrypted_data['signature'])
            sha512_hash = encrypted_data['sha512']
            sm3_hash = encrypted_data['sm3']
            
            # 生成预期的数字签名
            from encryption.hybrid_encryption import HybridEncryption
            hybrid_enc = HybridEncryption()
            expected_signature = hybrid_enc.generate_signature(c3 + sha512_hash.encode() + sm3_hash.encode(), master_key)
            
            # 验证数字签名
            if signature != expected_signature:
                self.errors.append("数字签名验证失败，加密产物可能被篡改")
                return False
            
            return True
        except Exception as e:
            self.errors.append(f"加密产物完整性验证失败: {str(e)}")
            return False
    
    def run_all_checks(self, encrypted_file, master_key=None):
        """
        运行所有解密前预检
        
        Args:
            encrypted_file (str): 加密产物路径
            master_key (bytes, optional): 主密钥，用于验证数字签名
        
        Returns:
            bool: 所有检查是否通过
        """
        # 重置错误和警告列表
        self.errors = []
        self.warnings = []
        
        print("开始解密前预检...")
        
        # 检查1: 工具完整性
        print("  1. 检查解密工具完整性...")
        tool_check = self.check_tool_integrity()
        
        # 检查2: 加密产物完整性
        print("  2. 检查加密产物完整性...")
        file_check = self.check_encrypted_file(encrypted_file)
        
        # 检查3: 加密产物数字签名验证（如果提供了主密钥）
        signature_check = True
        if master_key:
            print("  3. 验证加密产物数字签名...")
            signature_check = self.verify_encrypted_file_integrity(encrypted_file, master_key)
        
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
        all_passed = tool_check and file_check and signature_check
        
        if all_passed:
            print("\n✓ 所有预检通过，可以开始解密")
        else:
            print("\n✗ 预检失败，无法开始解密")
        
        return all_passed
