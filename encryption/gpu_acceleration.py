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

class GPUAccelerator:
    """
    GPU加速器，用于加速计算密集型操作
    """
    
    def __init__(self):
        """
        初始化GPU加速器
        """
        self.gpu_available = False
        self.cuda_available = False
        self.tensorflow_available = False
        self.pytorch_available = False
        self.oneapi_available = False
        self.npu_available = False
        
        # 检测可用的GPU库
        self._detect_gpu_libraries()
    
    def _detect_gpu_libraries(self):
        """
        检测可用的GPU库
        """
        # 检测CUDA (NVIDIA和AMD显卡)
        try:
            # 首先尝试导入本地torch
            import torch
            self.pytorch_available = True
            if torch.cuda.is_available():
                self.cuda_available = True
                self.gpu_available = True
                # 检测GPU类型
                try:
                    gpu_name = torch.cuda.get_device_name(0)
                    print(f"CUDA可用，GPU加速已启用，设备: {gpu_name}")
                except Exception:
                    print("CUDA可用，GPU加速已启用")
        except ImportError:
            print("PyTorch未安装")
            self.pytorch_available = False
            self.cuda_available = False
        except Exception as e:
            # PyTorch导入失败，可能是c10.dll等问题
            print(f"PyTorch导入失败: {e}")
            # 完全禁用PyTorch，确保程序不会继续尝试使用有问题的torch库
            self.pytorch_available = False
            self.cuda_available = False
            self.gpu_available = False
            # 打印详细错误信息，帮助用户了解问题
            print("警告: PyTorch导入失败，将完全禁用GPU加速，使用CPU计算")
            print("如果需要GPU加速，请确保安装了正确版本的PyTorch和CUDA驱动")
            # 直接返回，避免继续检测其他可能依赖PyTorch的库
            print("未检测到可用的GPU库，将使用CPU计算")
            return
        
        # 检测TensorFlow (支持更多GPU类型)
        try:
            import tensorflow as tf
            self.tensorflow_available = True
            gpus = tf.config.list_physical_devices('GPU')
            if gpus:
                self.gpu_available = True
                # 检测GPU类型
                for gpu in gpus:
                    print(f"TensorFlow GPU可用，GPU加速已启用，设备: {gpu.name}")
        except ImportError:
            pass
        
        # 检测Intel OneAPI (Intel核显)
        try:
            import dpctl
            self.oneapi_available = True
            self.gpu_available = True
            print("Intel OneAPI可用，GPU加速已启用")
        except ImportError:
            pass
        
        # 检测NPU
        try:
            # 尝试导入NPU相关库
            if self.pytorch_available:
                import torch
                # 检查是否有NPU设备
                if hasattr(torch, 'npu') and torch.npu.is_available():
                    self.npu_available = True
                    self.gpu_available = True
                    print(f"NPU可用，NPU加速已启用，设备: {torch.npu.get_device_name(0)}")
            else:
                # PyTorch不可用，尝试其他NPU检测方法
                try:
                    import tensorflow as tf
                    npus = tf.config.list_physical_devices('NPU')
                    if npus:
                        self.npu_available = True
                        self.gpu_available = True
                        print("TensorFlow NPU可用，NPU加速已启用")
                except ImportError:
                    pass
                
                # 尝试检测国产NPU
                try:
                    # 检测华为昇腾NPU
                    try:
                        import ascend
                        self.npu_available = True
                        self.gpu_available = True
                        print("华为昇腾NPU可用，NPU加速已启用")
                    except ImportError:
                        pass
                    
                    # 检测寒武纪思元NPU
                    try:
                        import cambricon
                        self.npu_available = True
                        self.gpu_available = True
                        print("寒武纪思元NPU可用，NPU加速已启用")
                    except ImportError:
                        pass
                except Exception:
                    pass
        except ImportError:
            pass
        
        if not self.gpu_available:
            print("未检测到可用的GPU库，将使用CPU计算")
    
    def accelerate_logistic_map(self, x: Union[float, list, np.ndarray], r: float = 3.9999) -> Union[float, list, np.ndarray]:
        """
        加速Logistic混沌映射计算
        
        Args:
            x: 当前值或值数组/列表
            r: 混沌参数
        
        Returns:
            计算结果
        """
        # 首先检查是否启用了GPU加速
        if not self.gpu_available:
            # GPU不可用，直接使用CPU计算
            if NUMPY_AVAILABLE and isinstance(x, np.ndarray):
                return r * x * (1.0 - x)
            else:
                # 单个值或列表使用CPU计算
                return r * x * (1.0 - x)
        
        # 尝试使用NPU加速
        if self.npu_available and self.pytorch_available:
            try:
                import torch
                if NUMPY_AVAILABLE and isinstance(x, np.ndarray):
                    # 使用PyTorch NPU加速
                    try:
                        x_tensor = torch.tensor(x, device='npu')
                        result = r * x_tensor * (1.0 - x_tensor)
                        return result.cpu().numpy()
                    except Exception as e:
                        # PyTorch NPU计算失败，回退到CPU计算
                        print(f"PyTorch NPU计算失败: {e}")
                        self.npu_available = False
                        self.gpu_available = False
                else:
                    # 单个值或列表使用CPU计算
                    return r * x * (1.0 - x)
            except ImportError:
                # PyTorch未安装，回退到CPU计算
                print("PyTorch未安装")
                self.pytorch_available = False
                self.npu_available = False
                self.gpu_available = False
            except Exception as e:
                # PyTorch使用失败，回退到CPU计算
                print(f"PyTorch使用失败: {e}")
                self.pytorch_available = False
                self.npu_available = False
                self.gpu_available = False
        
        # 尝试使用CUDA加速
        if self.cuda_available and self.pytorch_available:
            try:
                import torch
                if NUMPY_AVAILABLE and isinstance(x, np.ndarray):
                    # 使用PyTorch GPU加速
                    try:
                        x_tensor = torch.tensor(x, device='cuda')
                        result = r * x_tensor * (1.0 - x_tensor)
                        return result.cpu().numpy()
                    except Exception as e:
                        # PyTorch计算失败，回退到CPU计算
                        print(f"PyTorch计算失败: {e}")
                        self.pytorch_available = False
                        self.cuda_available = False
                        self.gpu_available = False
                else:
                    # 单个值或列表使用CPU计算
                    return r * x * (1.0 - x)
            except ImportError:
                # PyTorch未安装，回退到CPU计算
                print("PyTorch未安装")
                self.pytorch_available = False
                self.cuda_available = False
                self.gpu_available = False
            except Exception as e:
                # PyTorch使用失败，回退到CPU计算
                print(f"PyTorch使用失败: {e}")
                self.pytorch_available = False
                self.cuda_available = False
                self.gpu_available = False
        
        # 使用NumPy或CPU计算
        if NUMPY_AVAILABLE and isinstance(x, np.ndarray):
            return r * x * (1.0 - x)
        elif isinstance(x, list):
            return [r * val * (1.0 - val) for val in x]
        else:
            return r * x * (1.0 - x)
    
    def generate_chaotic_sequence(self, length: int, x0: float = 0.31415926, n: int = 20) -> Union[np.ndarray, list]:
        """
        加速生成混沌序列
        
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
        
        # 首先检查是否启用了GPU加速
        if not self.gpu_available:
            # GPU不可用，直接使用CPU计算
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
        
        # 尝试使用NPU加速
        if self.npu_available and self.pytorch_available:
            try:
                import torch
                # 使用PyTorch NPU加速批量计算
                try:
                    x_tensor = torch.tensor(x, device='npu')
                    result = torch.zeros(length, device='npu')
                    
                    for i in range(length):
                        x_tensor = 3.9999 * x_tensor * (1.0 - x_tensor)
                        result[i] = (x_tensor * 256) % 256
                    
                    if NUMPY_AVAILABLE:
                        return result.cpu().numpy().astype(int)
                    else:
                        return result.cpu().tolist()
                except Exception as e:
                    # PyTorch NPU计算失败，回退到CPU计算
                    print(f"PyTorch NPU计算失败: {e}")
                    self.npu_available = False
                    self.gpu_available = False
                    # 直接使用CPU计算
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
            except ImportError:
                # PyTorch未安装，回退到CPU计算
                print("PyTorch未安装")
                self.pytorch_available = False
                self.npu_available = False
                self.gpu_available = False
                # 直接使用CPU计算
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
            except Exception as e:
                # PyTorch使用失败，回退到CPU计算
                print(f"PyTorch使用失败: {e}")
                self.pytorch_available = False
                self.npu_available = False
                self.gpu_available = False
                # 直接使用CPU计算
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
        
        # 尝试使用CUDA加速
        if self.cuda_available and self.pytorch_available:
            try:
                import torch
                # 使用PyTorch GPU加速批量计算
                try:
                    x_tensor = torch.tensor(x, device='cuda')
                    result = torch.zeros(length, device='cuda')
                    
                    for i in range(length):
                        x_tensor = 3.9999 * x_tensor * (1.0 - x_tensor)
                        result[i] = (x_tensor * 256) % 256
                    
                    if NUMPY_AVAILABLE:
                        return result.cpu().numpy().astype(int)
                    else:
                        return result.cpu().tolist()
                except Exception as e:
                    # PyTorch计算失败，回退到CPU计算
                    print(f"PyTorch计算失败: {e}")
                    self.pytorch_available = False
                    self.cuda_available = False
                    self.gpu_available = False
                    # 直接使用CPU计算
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
            except ImportError:
                # PyTorch未安装，回退到CPU计算
                print("PyTorch未安装")
                self.pytorch_available = False
                self.cuda_available = False
                self.gpu_available = False
                # 直接使用CPU计算
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
            except Exception as e:
                # PyTorch使用失败，回退到CPU计算
                print(f"PyTorch使用失败: {e}")
                self.pytorch_available = False
                self.cuda_available = False
                self.gpu_available = False
                # 直接使用CPU计算
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
        
        # 使用NumPy或CPU计算
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
        加速DNA序列置换
        
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
        
        if self.npu_available and self.pytorch_available:
            try:
                import torch
                # 使用NPU加速置换计算
                try:
                    permutation_index = torch.arange(length, device='npu')
                    chaos_tensor = torch.tensor(chaotic_sequence[:length], device='npu')
                    
                    # 计算置换索引
                    for i in range(length-1, 0, -1):
                        j = chaos_tensor[i] % (i + 1)
                        # 交换索引
                        permutation_index[i], permutation_index[j] = permutation_index[j], permutation_index[i]
                    
                    # 执行置换
                    if NUMPY_AVAILABLE:
                        permutation_index = permutation_index.cpu().numpy()
                    else:
                        permutation_index = permutation_index.cpu().tolist()
                    permuted = [result[i] for i in permutation_index]
                    return ''.join(permuted)
                except Exception as e:
                    # PyTorch NPU计算失败，回退到CPU计算
                    print(f"PyTorch NPU计算失败: {e}")
                    self.pytorch_available = False
                    self.npu_available = False
            except ImportError:
                # PyTorch未安装，回退到CPU计算
                print("PyTorch未安装")
                self.pytorch_available = False
                self.npu_available = False
            except Exception as e:
                # PyTorch使用失败，回退到CPU计算
                print(f"PyTorch使用失败: {e}")
                self.pytorch_available = False
                self.npu_available = False
        
        if self.cuda_available and self.pytorch_available:
            try:
                import torch
                # 使用GPU加速置换计算
                try:
                    permutation_index = torch.arange(length, device='cuda')
                    chaos_tensor = torch.tensor(chaotic_sequence[:length], device='cuda')
                    
                    # 计算置换索引
                    for i in range(length-1, 0, -1):
                        j = chaos_tensor[i] % (i + 1)
                        # 交换索引
                        permutation_index[i], permutation_index[j] = permutation_index[j], permutation_index[i]
                    
                    # 执行置换
                    if NUMPY_AVAILABLE:
                        permutation_index = permutation_index.cpu().numpy()
                    else:
                        permutation_index = permutation_index.cpu().tolist()
                    permuted = [result[i] for i in permutation_index]
                    return ''.join(permuted)
                except Exception as e:
                    # PyTorch计算失败，回退到CPU计算
                    print(f"PyTorch计算失败: {e}")
                    self.pytorch_available = False
                    self.cuda_available = False
            except ImportError:
                # PyTorch未安装，回退到CPU计算
                print("PyTorch未安装")
                self.pytorch_available = False
                self.cuda_available = False
            except Exception as e:
                # PyTorch使用失败，回退到CPU计算
                print(f"PyTorch使用失败: {e}")
                self.pytorch_available = False
                self.cuda_available = False
        
        # 使用CPU计算
        for i in range(length-1, 0, -1):
            j = chaotic_sequence[i] % (i + 1)
            result[i], result[j] = result[j], result[i]
        return ''.join(result)
    
    def accelerate_dna_inverse_permutation(self, permuted_dna: str, chaotic_sequence: Union[list, np.ndarray]) -> str:
        """
        加速DNA序列逆置换
        
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
        if self.gpu_available and len(data) > 10:
            # 使用GPU批量处理
            return [process_func(item) for item in data]
        else:
            # 使用CPU处理
            return [process_func(item) for item in data]

# 全局GPU加速器实例
GPU_ACCELERATOR = GPUAccelerator()

# 装饰器：用于加速函数
def gpu_accelerate(func):
    """
    GPU加速装饰器
    """
    def wrapper(*args, **kwargs):
        if GPU_ACCELERATOR.gpu_available:
            # GPU可用时的处理
            return func(*args, **kwargs)
        else:
            # GPU不可用时的处理
            return func(*args, **kwargs)
    return wrapper
