from utils.random_generator import generate_secure_key
from utils.memory_cleaner import clear_memory

class QuantumKeyGenerator:
    """
    量子密钥生成器的替代方案，使用密码学安全的随机数生成器模拟量子密钥
    """
    
    def __init__(self, min_key_length=128):
        """
        初始化量子密钥生成器
        
        Args:
            min_key_length (int, optional): 最小密钥长度（字节），默认128字节（1024位）
        """
        self.min_key_length = min_key_length
    
    def generate_quantum_key(self, key_length=None):
        """
        生成量子密钥
        
        Args:
            key_length (int, optional): 密钥长度（字节），如果为None则使用最小密钥长度
        
        Returns:
            bytes: 生成的量子密钥
        """
        if key_length is None:
            key_length = self.min_key_length
        elif key_length < self.min_key_length:
            raise ValueError(f"密钥长度必须大于等于{self.min_key_length}字节")
        
        # 使用密码学安全的随机数生成器生成量子密钥
        return generate_secure_key(key_length)
    
    def encapsulate_key(self, quantum_key, receiver_public_key):
        """
        使用接收方公钥封装量子密钥
        
        Args:
            quantum_key (bytes): 量子密钥
            receiver_public_key (bytes): 接收方公钥
        
        Returns:
            bytes: 封装后的量子密钥
        """
        # 这里使用简单的异或操作模拟非对称加密封装
        # 优化：使用更高效的异或实现
        key_length = len(quantum_key)
        public_key_len = len(receiver_public_key)
        
        # 优化：预分配结果缓冲区
        result = bytearray(key_length)
        
        # 优化：避免创建中间重复密钥，直接在异或时重复使用公钥
        for i in range(key_length):
            result[i] = quantum_key[i] ^ receiver_public_key[i % public_key_len]
        
        # 转换为bytes并返回
        return bytes(result)
    
    def decapsulate_key(self, encapsulated_key, receiver_private_key):
        """
        使用接收方私钥解封装量子密钥
        
        Args:
            encapsulated_key (bytes): 封装后的量子密钥
            receiver_private_key (bytes): 接收方私钥
        
        Returns:
            bytes: 解封装后的量子密钥
        """
        # 这里使用简单的异或操作模拟非对称解密解封装
        # 优化：使用更高效的异或实现
        key_length = len(encapsulated_key)
        private_key_len = len(receiver_private_key)
        
        # 优化：预分配结果缓冲区
        result = bytearray(key_length)
        
        # 优化：避免创建中间重复密钥，直接在异或时重复使用私钥
        for i in range(key_length):
            result[i] = encapsulated_key[i] ^ receiver_private_key[i % private_key_len]
        
        # 转换为bytes并返回
        return bytes(result)
    
    def generate_session_key(self, quantum_key, master_key):
        """
        使用主密钥和量子密钥生成会话密钥
        
        Args:
            quantum_key (bytes): 量子密钥
            master_key (bytes): 主密钥
        
        Returns:
            bytes: 生成的会话密钥
        """
        # 使用异或操作生成会话密钥
        # 优化：使用更高效的异或实现
        key_length = len(quantum_key)
        master_key_len = len(master_key)
        
        # 优化：预分配结果缓冲区
        result = bytearray(key_length)
        
        # 优化：避免创建中间重复密钥，直接在异或时重复使用主密钥
        for i in range(key_length):
            result[i] = quantum_key[i] ^ master_key[i % master_key_len]
        
        # 转换为bytes并返回
        return bytes(result)
