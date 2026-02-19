#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
哈希计算模块
负责计算文件和目录的哈希值，支持SHA-256和SM3等算法
"""

import os
import hashlib
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def calculate_hash(file_path, algorithm='sha256', block_size=65536):
    """
    计算文件的哈希值
    
    Args:
        file_path (str): 文件路径
        algorithm (str): 哈希算法，支持'sha256'和'sm3'
        block_size (int): 读取文件的块大小
    
    Returns:
        str: 文件的哈希值
    """
    try:
        # 选择哈希算法
        if algorithm.lower() == 'sha256':
            hash_obj = hashlib.sha256()
        elif algorithm.lower() == 'sm3':
            # 尝试导入SM3算法
            try:
                from Cryptodome.Hash import SM3
                hash_obj = SM3.new()
            except ImportError:
                logger.warning("SM3算法不可用，回退到SHA-256")
                hash_obj = hashlib.sha256()
        else:
            logger.warning(f"不支持的哈希算法: {algorithm}，使用SHA-256")
            hash_obj = hashlib.sha256()
        
        # 读取文件并计算哈希值
        with open(file_path, 'rb') as f:
            while True:
                data = f.read(block_size)
                if not data:
                    break
                hash_obj.update(data)
        
        return hash_obj.hexdigest()
    except Exception as e:
        logger.error(f"计算文件哈希值时出错: {e}")
        return None

def calculate_hash_pair(file_path):
    """
    计算文件的SHA-256和SM3哈希值对
    
    Args:
        file_path (str): 文件路径
    
    Returns:
        dict: 包含SHA-256和SM3哈希值的字典
    """
    sha256_hash = calculate_hash(file_path, 'sha256')
    sm3_hash = calculate_hash(file_path, 'sm3')
    
    return {
        'sha256': sha256_hash,
        'sm3': sm3_hash
    }

def calculate_directory_hash(directory_path, algorithm='sha256', exclude=None):
    """
    计算目录的哈希值
    递归计算目录中所有文件的哈希值，然后将这些哈希值组合计算出目录的哈希值
    
    Args:
        directory_path (str): 目录路径
        algorithm (str): 哈希算法，支持'sha256'和'sm3'
        exclude (list): 要排除的文件或目录列表
    
    Returns:
        dict: 包含目录哈希值和文件哈希值的字典
    """
    if exclude is None:
        exclude = []
    
    # 选择哈希算法
    if algorithm.lower() == 'sha256':
        hash_obj = hashlib.sha256()
    elif algorithm.lower() == 'sm3':
        # 尝试导入SM3算法
        try:
            from Cryptodome.Hash import SM3
            hash_obj = SM3.new()
        except ImportError:
            logger.warning("SM3算法不可用，回退到SHA-256")
            hash_obj = hashlib.sha256()
    else:
        logger.warning(f"不支持的哈希算法: {algorithm}，使用SHA-256")
        hash_obj = hashlib.sha256()
    
    file_hashes = {}
    
    try:
        # 递归遍历目录
        for root, dirs, files in os.walk(directory_path):
            # 排除指定的目录
            dirs[:] = [d for d in dirs if d not in exclude]
            
            for file_name in files:
                # 排除指定的文件
                if file_name in exclude:
                    continue
                
                file_path = os.path.join(root, file_name)
                # 计算文件的哈希值
                file_hash = calculate_hash(file_path, algorithm)
                if file_hash:
                    # 计算相对路径
                    relative_path = os.path.relpath(file_path, directory_path)
                    file_hashes[relative_path] = file_hash
                    # 将文件路径和哈希值添加到目录哈希计算中
                    hash_obj.update(relative_path.encode('utf-8'))
                    hash_obj.update(file_hash.encode('utf-8'))
        
        return {
            'directory_hash': hash_obj.hexdigest(),
            'file_hashes': file_hashes
        }
    except Exception as e:
        logger.error(f"计算目录哈希值时出错: {e}")
        return {
            'directory_hash': None,
            'file_hashes': {}
        }

def verify_file_integrity(file_path, expected_hash, algorithm='sha256'):
    """
    验证文件的完整性
    
    Args:
        file_path (str): 文件路径
        expected_hash (str): 预期的哈希值
        algorithm (str): 哈希算法
    
    Returns:
        bool: 文件完整性是否验证通过
    """
    actual_hash = calculate_hash(file_path, algorithm)
    if actual_hash:
        return actual_hash == expected_hash
    return False

def verify_directory_integrity(directory_path, expected_hash, algorithm='sha256', exclude=None):
    """
    验证目录的完整性
    
    Args:
        directory_path (str): 目录路径
        expected_hash (str): 预期的哈希值
        algorithm (str): 哈希算法
        exclude (list): 要排除的文件或目录列表
    
    Returns:
        bool: 目录完整性是否验证通过
    """
    result = calculate_directory_hash(directory_path, algorithm, exclude)
    if result['directory_hash']:
        return result['directory_hash'] == expected_hash
    return False

def generate_hash_report(file_path):
    """
    生成文件的哈希值报告
    
    Args:
        file_path (str): 文件路径
    
    Returns:
        dict: 包含文件信息和哈希值的报告
    """
    try:
        file_info = {
            'file_path': file_path,
            'file_size': os.path.getsize(file_path),
            'last_modified': os.path.getmtime(file_path)
        }
        
        hash_values = calculate_hash_pair(file_path)
        
        return {
            'file_info': file_info,
            'hashes': hash_values
        }
    except Exception as e:
        logger.error(f"生成哈希报告时出错: {e}")
        return None

def batch_calculate_hashes(file_list, algorithm='sha256'):
    """
    批量计算文件的哈希值
    
    Args:
        file_list (list): 文件路径列表
        algorithm (str): 哈希算法
    
    Returns:
        dict: 包含文件路径和对应哈希值的字典
    """
    results = {}
    
    for file_path in file_list:
        if os.path.isfile(file_path):
            hash_value = calculate_hash(file_path, algorithm)
            results[file_path] = hash_value
        else:
            logger.warning(f"文件不存在: {file_path}")
            results[file_path] = None
    
    return results

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # 计算指定文件的哈希值
        file_path = sys.argv[1]
        print(f"计算文件 {file_path} 的哈希值...")
        
        # 计算哈希值对
        hash_pair = calculate_hash_pair(file_path)
        print(f"SHA-256: {hash_pair['sha256']}")
        print(f"SM3: {hash_pair['sm3']}")
    else:
        # 测试功能
        print("哈希计算器测试")
        print("1. 计算文件哈希值")
        print("2. 计算目录哈希值")
        choice = input("请选择测试功能 (1/2): ")
        
        if choice == '1':
            test_file = input("请输入测试文件路径: ")
            if os.path.isfile(test_file):
                hash_result = calculate_hash(test_file)
                print(f"文件哈希值: {hash_result}")
            else:
                print("文件不存在")
        elif choice == '2':
            test_dir = input("请输入测试目录路径: ")
            if os.path.isdir(test_dir):
                hash_result = calculate_directory_hash(test_dir)
                print(f"目录哈希值: {hash_result['directory_hash']}")
                print(f"包含 {len(hash_result['file_hashes'])} 个文件")
            else:
                print("目录不存在")
        else:
            print("无效选择")
