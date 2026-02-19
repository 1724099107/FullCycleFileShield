from encryption.hybrid_encryption import HybridEncryption

class HybridDecryption:
    """
    混合解密模块，实现三层解密架构
    """
    
    def __init__(self):
        """
        初始化解密模块
        """
        self.hybrid_enc = HybridEncryption()
    
    def decrypt(self, encrypted_file, master_key, output_file=None):
        """
        执行混合解密
        
        Args:
            encrypted_file (str): 加密产物路径
            master_key (bytes): 主密钥
            output_file (str, optional): 输出解密文件路径，默认在当前目录生成
        
        Returns:
            tuple: (解密后的压缩包路径, sha512_hash, sm3_hash)
        """
        try:
            # 使用加密模块中的混合解密方法
            decrypted_file = self.hybrid_enc.decrypt(encrypted_file, master_key, output_file)
            
            # 获取解密后的压缩包的哈希值
            from utils.hash_calculator import calculate_hash_pair
            sha512_hash, sm3_hash = calculate_hash_pair(decrypted_file)
            
            return (decrypted_file, sha512_hash, sm3_hash)
        except Exception as e:
            raise RuntimeError(f"混合解密失败: {str(e)}")
