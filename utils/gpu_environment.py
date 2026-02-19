#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GPU环境初始化和设备检测模块
负责检测和管理GPU资源，提供设备选择功能
"""

import os
import sys
import platform
import logging

# 添加离线依赖目录到Python模块搜索路径（确保优先使用）
script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
offline_deps_dir = os.path.join(script_dir, "offline_deps")

if os.path.exists(offline_deps_dir):
    # 确保离线依赖目录在sys.path的最前面
    if offline_deps_dir not in sys.path:
        sys.path.insert(0, offline_deps_dir)
    else:
        # 如果已经存在，移到最前面
        sys.path.remove(offline_deps_dir)
        sys.path.insert(0, offline_deps_dir)

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 检查Python版本
required_python_version = (3, 12, 0)
current_python_version = tuple(map(int, platform.python_version().split('.')))

if current_python_version < required_python_version:
    logger.warning(f"Python版本低于要求的{required_python_version[0]}.{required_python_version[1]}.{required_python_version[2]}")
    logger.warning(f"当前Python版本: {platform.python_version()}")

def initialize_gpu():
    """
    初始化GPU环境
    尝试导入GPU相关库，失败则回退到CPU
    
    Returns:
        dict: 包含GPU环境信息的字典
    """
    gpu_info = {
        'available': False,
        'devices': [],
        'selected_device': None,
        'backend': 'CPU'
    }
    
    try:
        # 检查离线依赖目录中是否有PyTorch
        torch_available = False
        if os.path.exists(offline_deps_dir):
            if os.path.exists(os.path.join(offline_deps_dir, "torch")):
                torch_available = True
        
        # 只有当PyTorch可用时，才尝试导入
        if torch_available:
            # 尝试导入PyTorch
            logger.info("尝试导入PyTorch...")
            
            # 保存原始sys.path和PATH环境变量
            original_path = sys.path.copy()
            original_path_env = os.environ.get('PATH', '')
            
            # 确保离线依赖目录在sys.path的最前面
            if offline_deps_dir not in sys.path:
                sys.path.insert(0, offline_deps_dir)
            else:
                sys.path.remove(offline_deps_dir)
                sys.path.insert(0, offline_deps_dir)
            
            # 修改PATH环境变量，确保使用我们的离线依赖目录中的DLL文件
            torch_lib_dir = os.path.join(offline_deps_dir, "torch", "lib")
            if os.path.exists(torch_lib_dir):
                os.environ['PATH'] = torch_lib_dir + ';' + original_path_env
            
            # 打印调试信息
            logger.info(f"当前Python版本: {platform.python_version()}")
            logger.info(f"离线依赖目录: {offline_deps_dir}")
            logger.info(f"PyTorch库目录: {torch_lib_dir}")
            
            # 尝试导入PyTorch
            try:
                # 首先尝试直接导入PyTorch
                import torch
                logger.info(f"PyTorch导入成功，版本: {torch.__version__}")
                
                # 检查是否为CPU版本
                if '+cpu' in torch.__version__:
                    logger.info("PyTorch CPU版本，回退到CPU")
                else:
                    # 尝试检查CUDA可用性，但如果失败则回退到CPU
                    try:
                        if torch.cuda.is_available():
                            gpu_info['available'] = True
                            gpu_info['backend'] = 'PyTorch'
                            gpu_info['devices'] = [f'CUDA:{i}' for i in range(torch.cuda.device_count())]
                            gpu_info['selected_device'] = f'CUDA:{torch.cuda.current_device()}'
                            logger.info(f"PyTorch GPU可用: {gpu_info['devices']}")
                        else:
                            logger.info("PyTorch GPU不可用，回退到CPU")
                    except Exception as e:
                        logger.info(f"PyTorch CUDA检查失败，回退到CPU: {e}")
            except ImportError as e:
                # 如果直接导入失败，说明系统中没有安装PyTorch
                logger.info(f"直接导入PyTorch失败: {e}")
            except Exception as e:
                # 如果是DLL加载失败，这可能是因为PyTorch版本与Python版本不兼容
                if "DLL" in str(e) or "dll" in str(e):
                    logger.info(f"PyTorch DLL加载失败: {e}")
                    logger.info("这可能是因为PyTorch版本与当前Python版本不兼容")
                    logger.info(f"当前Python版本: {platform.python_version()}")
                    logger.info("尝试使用CPU模式运行...")
                else:
                    logger.info(f"PyTorch初始化失败，回退到CPU: {e}")
            finally:
                # 恢复原始sys.path
                sys.path = original_path
                # 恢复原始PATH环境变量
                os.environ['PATH'] = original_path_env
        else:
            # 如果PyTorch不可用，直接回退到CPU
            logger.info("PyTorch不可用，回退到CPU")
    except Exception as e:
        logger.info(f"PyTorch初始化失败，回退到CPU: {e}")
        
    # 尝试导入其他GPU后端
    if not gpu_info['available']:
        try:
            # 尝试导入TensorFlow
            import tensorflow as tf
            if tf.config.list_physical_devices('GPU'):
                gpu_info['available'] = True
                gpu_info['backend'] = 'TensorFlow'
                gpu_info['devices'] = [f'TensorFlow:{i}' for i in range(len(tf.config.list_physical_devices('GPU')))]
                gpu_info['selected_device'] = gpu_info['devices'][0]
                logger.info(f"TensorFlow GPU可用: {gpu_info['devices']}")
            else:
                logger.info("TensorFlow GPU不可用，回退到CPU")
        except ImportError:
            logger.info("TensorFlow未安装，回退到CPU")
        except Exception as e:
            logger.warning(f"TensorFlow初始化失败: {str(e)}，回退到CPU")
    
    # 尝试检测国产NPU
    if not gpu_info['available']:
        try:
            # 尝试导入昇腾NPU
            import torch_npu
            if torch_npu.is_available():
                gpu_info['available'] = True
                gpu_info['backend'] = 'Ascend NPU'
                gpu_info['devices'] = [f'Ascend:{i}' for i in range(torch_npu.device_count())]
                gpu_info['selected_device'] = f'Ascend:{torch_npu.current_device()}'
                logger.info(f"昇腾NPU可用: {gpu_info['devices']}")
        except ImportError:
            logger.info("昇腾NPU未安装，回退到CPU")
        except Exception as e:
            logger.warning(f"昇腾NPU初始化失败: {str(e)}，回退到CPU")
    
    # 尝试使用ONNX Runtime with DirectML (支持Intel核显)
    if not gpu_info['available']:
        try:
            import onnxruntime as ort
            available_providers = ort.get_available_providers()
            if 'DmlExecutionProvider' in available_providers:
                gpu_info['available'] = True
                gpu_info['backend'] = 'ONNX Runtime with DirectML'
                gpu_info['devices'] = ['DirectML:0']  # DirectML自动管理设备
                gpu_info['selected_device'] = 'DirectML:0'
                logger.info("ONNX Runtime with DirectML可用，已启用Intel核显加速")
        except ImportError:
            logger.info("ONNX Runtime with DirectML未安装，回退到CPU")
        except Exception as e:
            logger.warning(f"ONNX Runtime with DirectML初始化失败: {str(e)}，回退到CPU")
    
    return gpu_info

def get_available_devices():
    """
    获取所有可用的计算设备
    
    Returns:
        list: 可用设备列表
    """
    gpu_info = initialize_gpu()
    if gpu_info['available']:
        return gpu_info['devices']
    else:
        return ['CPU']

def get_best_device():
    """
    获取最佳计算设备
    
    Returns:
        str: 最佳设备标识符
    """
    gpu_info = initialize_gpu()
    if gpu_info['selected_device']:
        return gpu_info['selected_device']
    else:
        return 'CPU'

def is_gpu_available():
    """
    检查GPU是否可用
    
    Returns:
        bool: GPU是否可用
    """
    gpu_info = initialize_gpu()
    return gpu_info['available']

def get_device_properties(device_id):
    """
    获取设备属性
    
    Args:
        device_id (str): 设备标识符
    
    Returns:
        dict: 设备属性字典
    """
    properties = {
        'device_id': device_id,
        'type': 'CPU',
        'memory': 0,
        'compute_capability': 'N/A'
    }
    
    if device_id.startswith('CUDA:'):
        try:
            import torch
            device_idx = int(device_id.split(':')[1])
            properties['type'] = 'GPU'
            properties['memory'] = torch.cuda.get_device_properties(device_idx).total_memory / (1024 ** 3)
            properties['compute_capability'] = f"{torch.cuda.get_device_properties(device_idx).major}.{torch.cuda.get_device_properties(device_idx).minor}"
        except:
            pass
    elif device_id.startswith('DirectML:'):
        try:
            properties['type'] = 'GPU'
            properties['memory'] = 0  # DirectML不直接暴露内存信息
            properties['compute_capability'] = 'DirectML'
        except:
            pass
    
    return properties

def set_preferred_device(device_id):
    """
    设置首选设备
    
    Args:
        device_id (str): 设备标识符
    
    Returns:
        bool: 设置是否成功
    """
    try:
        if device_id.startswith('CUDA:'):
            import torch
            device_idx = int(device_id.split(':')[1])
            if device_idx < torch.cuda.device_count():
                torch.cuda.set_device(device_idx)
                logger.info(f"已设置首选设备: {device_id}")
                return True
        elif device_id.startswith('DirectML:'):
            # DirectML不需要显式设置设备，它会自动管理
            logger.info(f"已设置首选设备: {device_id}")
            return True
        return False
    except:
        return False

# 为了兼容性，添加别名
init_gpu_environment = initialize_gpu
get_compute_device = get_best_device

if __name__ == "__main__":
    # 测试GPU环境初始化
    print("初始化GPU环境...")
    gpu_info = initialize_gpu()
    print(f"GPU可用: {gpu_info['available']}")
    print(f"后端: {gpu_info['backend']}")
    print(f"可用设备: {gpu_info['devices']}")
    print(f"选择的设备: {gpu_info['selected_device']}")
    
    # 测试设备检测
    print("\n获取最佳设备...")
    best_device = get_best_device()
    print(f"最佳设备: {best_device}")
    
    # 测试设备属性
    print("\n获取设备属性...")
    properties = get_device_properties(best_device)
    print(f"设备属性: {properties}")
    
    # 测试别名
    print("\n测试别名...")
    gpu_info_alias = init_gpu_environment()
    print(f"使用别名初始化GPU环境: {gpu_info_alias['available']}")
    compute_device_alias = get_compute_device()
    print(f"使用别名获取计算设备: {compute_device_alias}")
