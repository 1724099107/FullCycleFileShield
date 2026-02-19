#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
内存管理和清理模块
负责清理进程内存和虚拟内存，优化内存使用
"""

import os
import sys
import gc
import psutil
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def clear_memory():
    """
    清理内存
    执行垃圾回收，释放未使用的内存
    
    Returns:
        dict: 内存清理前后的状态
    """
    # 获取清理前的内存状态
    before = get_memory_status()
    
    # 执行垃圾回收
    gc.collect()
    
    # 获取清理后的内存状态
    after = get_memory_status()
    
    # 计算释放的内存
    freed = before['used_memory'] - after['used_memory']
    
    logger.info(f"内存清理完成，释放了 {freed:.2f} MB 内存")
    
    return {
        'before': before,
        'after': after,
        'freed': freed
    }

def clean_process_memory():
    """
    清理进程内存
    清理当前进程的内存使用
    
    Returns:
        dict: 进程内存清理前后的状态
    """
    # 获取当前进程
    process = psutil.Process(os.getpid())
    
    # 获取清理前的进程内存状态
    before = process.memory_info().rss / (1024 * 1024)  # 转换为MB
    
    # 执行垃圾回收
    gc.collect()
    
    # 获取清理后的进程内存状态
    after = process.memory_info().rss / (1024 * 1024)  # 转换为MB
    
    # 计算释放的内存
    freed = before - after
    
    logger.info(f"进程内存清理完成，释放了 {freed:.2f} MB 内存")
    
    return {
        'before': before,
        'after': after,
        'freed': freed
    }

def clean_virtual_memory():
    """
    清理虚拟内存
    尝试清理系统虚拟内存
    
    Returns:
        dict: 虚拟内存清理前后的状态
    """
    # 获取清理前的虚拟内存状态
    before = get_virtual_memory_status()
    
    # 执行垃圾回收
    gc.collect()
    
    # 尝试释放文件系统缓存（仅Linux）
    if sys.platform == 'linux':
        try:
            with open('/proc/sys/vm/drop_caches', 'w') as f:
                f.write('3')
            logger.info("已尝试清理Linux文件系统缓存")
        except:
            logger.info("无法清理Linux文件系统缓存")
    
    # 获取清理后的虚拟内存状态
    after = get_virtual_memory_status()
    
    logger.info("虚拟内存清理完成")
    
    return {
        'before': before,
        'after': after
    }

def get_memory_status():
    """
    获取内存状态
    
    Returns:
        dict: 内存状态字典
    """
    memory = psutil.virtual_memory()
    return {
        'total_memory': memory.total / (1024 * 1024),  # 转换为MB
        'used_memory': memory.used / (1024 * 1024),    # 转换为MB
        'available_memory': memory.available / (1024 * 1024),  # 转换为MB
        'memory_percent': memory.percent
    }

def get_virtual_memory_status():
    """
    获取虚拟内存状态
    
    Returns:
        dict: 虚拟内存状态字典
    """
    swap = psutil.swap_memory()
    return {
        'total_swap': swap.total / (1024 * 1024),  # 转换为MB
        'used_swap': swap.used / (1024 * 1024),    # 转换为MB
        'free_swap': swap.free / (1024 * 1024),    # 转换为MB
        'swap_percent': swap.percent
    }

def get_process_memory_usage():
    """
    获取当前进程的内存使用情况
    
    Returns:
        dict: 进程内存使用情况
    """
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    
    return {
        'rss': memory_info.rss / (1024 * 1024),  # 转换为MB
        'vms': memory_info.vms / (1024 * 1024),  # 转换为MB
        'shared': getattr(memory_info, 'shared', 0) / (1024 * 1024),  # 转换为MB
        'text': getattr(memory_info, 'text', 0) / (1024 * 1024),    # 转换为MB
        'data': getattr(memory_info, 'data', 0) / (1024 * 1024)     # 转换为MB
    }

def monitor_memory_usage(interval=1, duration=10):
    """
    监控内存使用情况
    
    Args:
        interval (int): 监控间隔（秒）
        duration (int): 监控持续时间（秒）
    
    Returns:
        list: 内存使用情况列表
    """
    import time
    
    memory_stats = []
    start_time = time.time()
    
    while time.time() - start_time < duration:
        memory_stats.append({
            'timestamp': time.time(),
            'memory': get_memory_status(),
            'process': get_process_memory_usage()
        })
        time.sleep(interval)
    
    return memory_stats

def optimize_memory_usage():
    """
    优化内存使用
    执行一系列内存优化操作
    
    Returns:
        dict: 优化前后的内存状态
    """
    # 获取优化前的状态
    before = {
        'system': get_memory_status(),
        'process': get_process_memory_usage(),
        'virtual': get_virtual_memory_status()
    }
    
    # 执行内存清理
    clear_memory()
    clean_process_memory()
    clean_virtual_memory()
    
    # 获取优化后的状态
    after = {
        'system': get_memory_status(),
        'process': get_process_memory_usage(),
        'virtual': get_virtual_memory_status()
    }
    
    logger.info("内存优化完成")
    
    return {
        'before': before,
        'after': after
    }

def clear_sensitive_data(data):
    """
    清除敏感数据
    安全地清除内存中的敏感数据，防止内存泄露
    
    Args:
        data: 要清除的敏感数据（可以是字符串、字节、列表等）
    
    Returns:
        None
    """
    try:
        # 对于不同类型的数据，使用不同的清除方法
        if isinstance(data, bytearray):
            # 对于bytearray，可以直接修改
            for i in range(len(data)):
                data[i] = 0
        elif isinstance(data, list):
            # 对于列表，递归清除每个元素
            for i in range(len(data)):
                clear_sensitive_data(data[i])
        elif isinstance(data, dict):
            # 对于字典，递归清除每个值
            for key in data:
                clear_sensitive_data(data[key])
        # 注意：对于字符串和bytes等不可变类型，无法直接修改
        # 这种情况下，建议用户不要将敏感数据存储为不可变类型，
        # 或者在使用后立即将变量设置为None
        
        logger.info("敏感数据清除完成")
    except Exception as e:
        logger.warning(f"清除敏感数据时出错: {str(e)}")

if __name__ == "__main__":
    # 测试内存清理
    print("测试内存清理...")
    result = clear_memory()
    print(f"清理前内存使用: {result['before']['used_memory']:.2f} MB")
    print(f"清理后内存使用: {result['after']['used_memory']:.2f} MB")
    print(f"释放内存: {result['freed']:.2f} MB")
    
    # 测试进程内存清理
    print("\n测试进程内存清理...")
    process_result = clean_process_memory()
    print(f"清理前进程内存使用: {process_result['before']:.2f} MB")
    print(f"清理后进程内存使用: {process_result['after']:.2f} MB")
    print(f"释放内存: {process_result['freed']:.2f} MB")
    
    # 测试虚拟内存清理
    print("\n测试虚拟内存清理...")
    virtual_result = clean_virtual_memory()
    print(f"清理前虚拟内存使用: {virtual_result['before']['used_swap']:.2f} MB")
    print(f"清理后虚拟内存使用: {virtual_result['after']['used_swap']:.2f} MB")
    
    # 测试内存优化
    print("\n测试内存优化...")
    optimize_result = optimize_memory_usage()
    print(f"优化前系统内存使用: {optimize_result['before']['system']['used_memory']:.2f} MB")
    print(f"优化后系统内存使用: {optimize_result['after']['system']['used_memory']:.2f} MB")
