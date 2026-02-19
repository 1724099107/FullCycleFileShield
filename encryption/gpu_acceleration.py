import os
import sys
from typing import Optional, List, Tuple, Union

# 延迟导入numpy
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    np = None

class CPUAccelerator:
    """
    CPU加速器，用于处理计算密集型操作
    """
    
    def __init__(self):
        """
        初始化CPU加速器
        """
        self.cpu_available = True
        print("CPU加速器已初始化，将使用CPU进行计算")
    
    def accelerate_logistic_map(self, x: Union[float, list, np.ndarray], r: float = 3.9999) -> Union[float, list, np.ndarray]:
        """
        计算Logistic混沌映射
        
        Args:
            x: 当前值或值数组/列表
            r: 混沌参数
        
        Returns:
            计算结果
        """
        # 直接使用CPU计算
        if NUMPY_AVAILABLE and isinstance(x, np.ndarray):
            return r * x * (1.0 - x)
        elif isinstance(x, list):
            return [r * val * (1.0 - val) for val in x]
        else:
            return r * x * (1.0 - x)
    
    def generate_chaotic_sequence(self, length: int, x0: float = 0.31415926, n: int = 20) -> Union[np.ndarray, list]:
        """
        生成混沌序列
        
        Args:
            length: 序列长度
            x0: 初始值
            n: 预热迭代次数
        
        Returns:
            混沌序列 (numpy数组或列表)
        """
        if length == 0:
            return np.array([]) if NUMPY_AVAILABLE else []
        
        # 预热计算
        x = x0
        for _ in range(n):
            x = self.accelerate_logistic_map(x)
        
        # 使用CPU计算
        if NUMPY_AVAILABLE:
            result = np.zeros(length, dtype=int)
            for i in range(length):
                x = 3.9999 * x * (1.0 - x)
                result[i] = int(x * 256) % 256
            return result
        else:
            # 不使用NumPy，使用列表
            result = []
            for i in range(length):
                x = 3.9999 * x * (1.0 - x)
                result.append(int(x * 256) % 256)
            return result
    
    def accelerate_dna_permutation(self, dna_sequence: str, chaotic_sequence: Union[list, np.ndarray]) -> str:
        """
        DNA序列置换
        
        Args:
            dna_sequence: DNA序列
            chaotic_sequence: 混沌序列 (列表或numpy数组)
        
        Returns:
            置换后的DNA序列
        """
        length = len(dna_sequence)
        if length == 0:
            return ""
        
        # 转换为列表以便修改
        result = list(dna_sequence)
        
        # 使用CPU计算
        for i in range(length-1, 0, -1):
            j = chaotic_sequence[i] % (i + 1)
            result[i], result[j] = result[j], result[i]
        return ''.join(result)
    
    def accelerate_dna_inverse_permutation(self, permuted_dna: str, chaotic_sequence: Union[list, np.ndarray]) -> str:
        """
        DNA序列逆置换
        
        Args:
            permuted_dna: 置换后的DNA序列
            chaotic_sequence: 混沌序列 (列表或numpy数组)
        
        Returns:
            逆置换后的DNA序列
        """
        length = len(permuted_dna)
        if length == 0:
            return ""
        
        # 计算置换索引
        permutation_index = list(range(length))
        
        # 计算置换索引
        for i in range(length-1, 0, -1):
            j = chaotic_sequence[i] % (i + 1)
            permutation_index[i], permutation_index[j] = permutation_index[j], permutation_index[i]
        
        # 执行逆置换
        permuted_list = list(permuted_dna)
        result = [''] * length
        
        for i in range(length):
            result[permutation_index[i]] = permuted_list[i]
        
        return ''.join(result)
    
    def batch_process(self, data: List[bytes], process_func: callable) -> List[bytes]:
        """
        批量处理数据
        
        Args:
            data: 数据列表
            process_func: 处理函数
        
        Returns:
            处理后的数据列表
        """
        # 使用CPU处理
        return [process_func(item) for item in data]

# 全局CPU加速器实例
GPU_ACCELERATOR = CPUAccelerator()
CPU_ACCELERATOR = GPU_ACCELERATOR

# 装饰器：用于统一处理函数
def cpu_accelerate(func):
    """
    CPU处理装饰器
    """
    def wrapper(*args, **kwargs):
        # 直接使用CPU处理
        return func(*args, **kwargs)
    return wrapper

# 为了兼容性，保留原装饰器名称
gpu_accelerate = cpu_accelerate
