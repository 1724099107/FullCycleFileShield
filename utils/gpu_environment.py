#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CPU环境管理模块
负责管理CPU计算环境，提供统一的设备接口
"""

import os
import sys
import platform
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 检查Python版本
required_python_version = (3, 12, 0)
current_python_version = tuple(map(int, platform.python_version().split('.')))

if current_python_version < required_python_version:
    logger.warning(f"Python版本低于要求的{required_python_version[0]}.{required_python_version[1]}.{required_python_version[2]}")
    logger.warning(f"当前Python版本: {platform.python_version()}")

def initialize_cpu():
    """
    初始化CPU环境
    
    Returns:
        dict: 包含CPU环境信息的字典
    """
    cpu_info = {
        'available': True,
        'devices': ['CPU'],
        'selected_device': 'CPU',
        'backend': 'CPU'
    }
    
    logger.info("CPU环境初始化完成")
    logger.info(f"当前计算设备: CPU")
    
    return cpu_info

def get_available_devices():
    """
    获取所有可用的计算设备
    
    Returns:
        list: 可用设备列表
    """
    return ['CPU']

def get_best_device():
    """
    获取最佳计算设备
    
    Returns:
        str: 最佳设备标识符
    """
    return 'CPU'

def is_cpu_available():
    """
    检查CPU是否可用
    
    Returns:
        bool: CPU是否可用
    """
    return True

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
        if device_id == 'CPU':
            logger.info(f"已设置首选设备: {device_id}")
            return True
        else:
            logger.warning(f"不支持的设备类型: {device_id}，将使用CPU")
            return False
    except:
        return False

# 为了兼容性，添加别名
init_gpu_environment = initialize_cpu
get_compute_device = get_best_device
is_gpu_available = is_cpu_available
initialize_gpu = initialize_cpu

if __name__ == "__main__":
    # 测试CPU环境初始化
    print("初始化CPU环境...")
    cpu_info = initialize_cpu()
    print(f"CPU可用: {cpu_info['available']}")
    print(f"后端: {cpu_info['backend']}")
    print(f"可用设备: {cpu_info['devices']}")
    print(f"选择的设备: {cpu_info['selected_device']}")
    
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
    cpu_info_alias = init_gpu_environment()
    print(f"使用别名初始化CPU环境: {cpu_info_alias['available']}")
    compute_device_alias = get_compute_device()
    print(f"使用别名获取计算设备: {compute_device_alias}")
