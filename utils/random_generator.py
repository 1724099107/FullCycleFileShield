#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
密码学安全的随机数生成器模块
提供用于加密操作的安全随机数生成功能
"""

import os
import secrets


def generate_secure_key(key_length):
    """
    生成密码学安全的随机密钥
    
    Args:
        key_length (int): 密钥长度（字节）
    
    Returns:
        bytes: 生成的随机密钥
    """
    try:
        # 使用secrets模块生成密码学安全的随机字节
        # secrets模块比os.urandom更适合密码学应用
        return secrets.token_bytes(key_length)
    except AttributeError:
        # 如果secrets模块不可用（较旧的Python版本），回退到os.urandom
        return os.urandom(key_length)


def generate_secure_random_int(min_val, max_val):
    """
    生成密码学安全的随机整数
    
    Args:
        min_val (int): 最小值（包含）
        max_val (int): 最大值（包含）
    
    Returns:
        int: 生成的随机整数
    """
    try:
        # 使用secrets模块生成密码学安全的随机整数
        return secrets.randbelow(max_val - min_val + 1) + min_val
    except AttributeError:
        # 如果secrets模块不可用，回退到使用os.urandom
        import random
        random.seed(os.urandom(32))
        return random.randint(min_val, max_val)


def generate_secure_random_string(length, charset=None):
    """
    生成密码学安全的随机字符串
    
    Args:
        length (int): 字符串长度
        charset (str, optional): 字符集，默认为字母数字
    
    Returns:
        str: 生成的随机字符串
    """
    if charset is None:
        # 默认字符集：大小写字母和数字
        charset = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    
    try:
        # 使用secrets模块生成密码学安全的随机字符串
        return ''.join(secrets.choice(charset) for _ in range(length))
    except AttributeError:
        # 如果secrets模块不可用，回退到使用os.urandom
        import random
        random.seed(os.urandom(32))
        return ''.join(random.choice(charset) for _ in range(length))
