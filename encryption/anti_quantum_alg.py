from .gpu_acceleration import GPU_ACCELERATOR

# 延迟导入numpy
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    np = None

class AntiQuantumAlgorithm:
    """
    基于混沌映射和DNA编码的抗量子算法
    """
    
    def __init__(self, x0=0.31415926, n=20):
        """
        初始化抗量子算法
        
        Args:
            x0 (float, optional): 混沌映射初始值，默认0.31415926
            n (int, optional): 混沌映射迭代次数，默认20
        """
        self.x0 = x0
        self.n = n  # 恢复原始迭代次数，确保解密正确性
        self.dna_bases = {'00': 'A', '01': 'T', '10': 'C', '11': 'G'}
        self.reverse_dna_bases = {'A': '00', 'T': '01', 'C': '10', 'G': '11'}
        # 引入混沌序列缓存，避免重复计算
        self.chaotic_sequence_cache = {}
        # 预计算每个字节对应的DNA碱基序列查找表
        self.byte_to_dna = [''.join(['A', 'T', 'C', 'G'][(byte >> (6 - i*2)) & 0b11] for i in range(4)) for byte in range(256)]
        # 预计算每个DNA碱基对应的二进制值查找表
        self.base_to_bin = {'A': 0, 'T': 1, 'C': 2, 'G': 3}
        # 初始化混沌映射，预热计算
        self._initialize_chaotic_map()
    
    def _initialize_chaotic_map(self):
        """
        初始化混沌映射，预热计算
        """
        # 预热混沌映射，计算初始状态
        x = self.x0
        for _ in range(self.n):
            x = self.logistic_map(x)
        # 存储预热后的状态
        self.preheated_x = x
    
    def logistic_map(self, x, r=3.9999):
        """
        Logistic混沌映射
        
        Args:
            x (float): 当前值
            r (float, optional): 混沌参数，默认3.9999
        
        Returns:
            float: 下一个混沌值
        """
        # 优化：使用局部变量和简化计算
        # 由于这个函数被调用次数非常多（超过2000万次），任何微小的优化都会带来显著的性能提升
        return r * x * (1.0 - x)
    
    def generate_chaotic_sequence(self, length):
        """
        生成混沌序列
        
        Args:
            length (int): 序列长度
        
        Returns:
            list: 混沌序列
        """
        # 优化：如果length为0，直接返回空列表
        if length == 0:
            return []
        
        # 优化：检查缓存中是否已有该长度的序列
        if length in self.chaotic_sequence_cache:
            return self.chaotic_sequence_cache[length].copy()
        
        # 使用GPU加速器生成混沌序列
        chaotic_sequence = GPU_ACCELERATOR.generate_chaotic_sequence(length, self.x0, self.n)
        
        # 转换为列表（只有当返回值是numpy数组时才调用tolist）
        if NUMPY_AVAILABLE and hasattr(chaotic_sequence, 'tolist'):
            chaotic_sequence = chaotic_sequence.tolist()
        
        # 缓存结果
        if length < 100000:  # 只缓存长度小于100000的序列，避免内存占用过大
            self.chaotic_sequence_cache[length] = chaotic_sequence
        
        return chaotic_sequence
    
    def binary_to_dna(self, binary_data):
        """
        将二进制数据转换为DNA序列
        
        Args:
            binary_data (bytes): 二进制数据
        
        Returns:
            str: DNA序列
        """
        # 优化：如果数据为空，直接返回空字符串
        if not binary_data:
            return ""
        
        # 优化：使用预计算的查找表，进一步提高性能
        # 预分配足够大的字符串缓冲区
        result = []
        result_append = result.append
        byte_to_dna = self.byte_to_dna
        
        # 优化：使用快速迭代和局部变量
        for byte in binary_data:
            # 直接使用预计算的查找表
            result_append(byte_to_dna[byte])
        
        # 优化：使用join方法一次性连接字符串
        return ''.join(result)
    
    def dna_to_binary(self, dna_sequence):
        """
        将DNA序列转换为二进制数据
        
        Args:
            dna_sequence (str): DNA序列
        
        Returns:
            bytes: 二进制数据
        """
        # 优化：如果序列为空，直接返回空字节
        if not dna_sequence:
            return b''
        
        # 优化：使用预计算的查找表和更高效的位运算
        # 预计算二进制位数和字节数
        length = len(dna_sequence)
        byte_count = (length + 3) // 4  # 每4个碱基对应1个字节
        
        # 预分配列表空间
        binary_parts = bytearray(byte_count)  # 使用bytearray更高效
        
        index = 0
        byte_value = 0
        bit_count = 0
        
        # 优化：使用局部变量缓存，减少属性查找
        dna_seq = dna_sequence
        base_to_bin = self.base_to_bin
        
        # 优化：使用快速循环结构和局部变量
        # 预计算DNA序列的长度，避免在循环中重复计算
        for i in range(length):
            # 优化：直接访问字符，避免索引操作
            base = dna_seq[i]
            # 获取对应的二进制值（0-3）
            bin_val = base_to_bin[base]
            
            # 将二进制值添加到当前字节
            # 优化：使用位运算的快速计算
            byte_value = (byte_value << 2) | bin_val
            bit_count += 2
            
            # 每8位组成一个字节
            if bit_count == 8:
                binary_parts[index] = byte_value
                index += 1
                byte_value = 0
                bit_count = 0
        
        # 处理剩余的位
        if bit_count > 0:
            byte_value <<= (8 - bit_count)
            binary_parts[index] = byte_value
        
        # 优化：直接返回bytearray的bytes转换
        return bytes(binary_parts)
    
    def dna_permutation(self, dna_sequence, chaotic_sequence):
        """
        使用混沌序列对DNA序列进行置换
        
        Args:
            dna_sequence (str): DNA序列
            chaotic_sequence (list): 混沌序列
        
        Returns:
            str: 置换后的DNA序列
        """
        length = len(dna_sequence)
        
        # 优化：如果序列为空，直接返回空字符串
        if length == 0:
            return ""
        
        # 使用GPU加速器进行置换
        if NUMPY_AVAILABLE:
            chaotic_array = np.array(chaotic_sequence, dtype=int)
            result = GPU_ACCELERATOR.accelerate_dna_permutation(dna_sequence, chaotic_array)
        else:
            # 不使用numpy，直接传递列表
            result = GPU_ACCELERATOR.accelerate_dna_permutation(dna_sequence, chaotic_sequence)
        
        return result
    
    def dna_inverse_permutation(self, permuted_dna, chaotic_sequence):
        """
        使用混沌序列对DNA序列进行逆置换
        
        Args:
            permuted_dna (str): 置换后的DNA序列
            chaotic_sequence (list): 混沌序列
        
        Returns:
            str: 逆置换后的DNA序列
        """
        length = len(permuted_dna)
        
        # 优化：如果长度为0，直接返回空字符串
        if length == 0:
            return ""
        
        # 使用GPU加速器进行逆置换
        if NUMPY_AVAILABLE:
            chaotic_array = np.array(chaotic_sequence, dtype=int)
            result = GPU_ACCELERATOR.accelerate_dna_inverse_permutation(permuted_dna, chaotic_array)
        else:
            # 不使用numpy，直接传递列表
            result = GPU_ACCELERATOR.accelerate_dna_inverse_permutation(permuted_dna, chaotic_sequence)
        
        return result
    
    def encrypt(self, plaintext):
        """
        加密数据
        
        Args:
            plaintext (bytes): 明文数据
        
        Returns:
            bytes: 加密后的数据
        """
        # 优化：如果明文为空，直接返回空字节
        if not plaintext:
            return b''
        
        # 1. 将明文转换为DNA序列
        dna_sequence = self.binary_to_dna(plaintext)
        
        # 2. 生成混沌序列
        chaotic_sequence = self.generate_chaotic_sequence(len(dna_sequence))
        
        # 3. 使用混沌序列对DNA序列进行置换
        permuted_dna = self.dna_permutation(dna_sequence, chaotic_sequence)
        
        # 4. 将置换后的DNA序列转换为二进制数据
        ciphertext = self.dna_to_binary(permuted_dna)
        
        return ciphertext
    
    def decrypt(self, ciphertext):
        """
        解密数据
        
        Args:
            ciphertext (bytes): 密文数据
        
        Returns:
            bytes: 解密后的数据
        """
        # 优化：如果密文为空，直接返回空字节
        if not ciphertext:
            return b''
        
        # 1. 将密文转换为DNA序列
        permuted_dna = self.binary_to_dna(ciphertext)
        
        # 2. 生成混沌序列（与加密时相同）
        # 优化：使用缓存的混沌序列，避免重复计算
        dna_length = len(permuted_dna)
        chaotic_sequence = self.generate_chaotic_sequence(dna_length)
        
        # 3. 使用混沌序列对DNA序列进行逆置换
        # 优化：直接在DNA序列上进行逆置换，避免额外的内存操作
        original_dna = self.dna_inverse_permutation(permuted_dna, chaotic_sequence)
        
        # 4. 将DNA序列转换为二进制数据
        plaintext = self.dna_to_binary(original_dna)
        
        return plaintext
