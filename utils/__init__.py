# utils module initialization file
"""
工具模块集合
包含CPU环境检测、内存清理、哈希计算和依赖检查等功能
"""

from .gpu_environment import (
    initialize_gpu, get_available_devices, get_best_device,
    is_gpu_available, get_device_properties, set_preferred_device,
    init_gpu_environment, get_compute_device
)
from .memory_cleaner import clear_memory, clean_process_memory, clean_virtual_memory, clear_sensitive_data
from .hash_calculator import calculate_hash, calculate_hash_pair, calculate_directory_hash
from .dependency_checker import check_dependencies, check_directory_structure, check_system_environment
from .random_generator import generate_secure_key, generate_secure_random_int, generate_secure_random_string

__all__ = [
    # CPU环境相关
    'initialize_gpu',
    'get_available_devices',
    'get_best_device',
    'is_gpu_available',
    'get_device_properties',
    'set_preferred_device',
    'init_gpu_environment',
    'get_compute_device',
    
    # 内存清理相关
    'clear_memory',
    'clean_process_memory',
    'clean_virtual_memory',
    'clear_sensitive_data',
    
    # 哈希计算相关
    'calculate_hash',
    'calculate_hash_pair',
    'calculate_directory_hash',
    
    # 依赖检查相关
    'check_dependencies',
    'check_directory_structure',
    'check_system_environment',
    
    # 随机数生成相关
    'generate_secure_key',
    'generate_secure_random_int',
    'generate_secure_random_string'
]

__version__ = '1.0.0'
