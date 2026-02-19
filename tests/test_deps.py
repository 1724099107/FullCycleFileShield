#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
依赖测试脚本
用于验证所有依赖是否正确安装
"""

import sys

def test_import(module_name):
    """
    测试导入模块
    """
    try:
        module = __import__(module_name)
        version = getattr(module, "__version__", "未知版本")
        print(f"[OK] {module_name} 导入成功 (版本: {version})")
        return True
    except ImportError as e:
        print(f"[ERROR] {module_name} 导入失败: {e}")
        return False

if __name__ == "__main__":
    print("开始测试依赖导入...")
    
    # 需要测试的模块列表
    modules = [
        "Cryptodome",  # pycryptodomex
        "py7zr",       # py7zr
        "psutil",      # psutil
        "PyQt5",       # PyQt5
        "numpy"        # numpy
    ]
    
    # 测试每个模块
    success_count = 0
    total_count = len(modules)
    
    for module in modules:
        if test_import(module):
            success_count += 1
    
    print(f"\n测试结果: {success_count}/{total_count} 个模块导入成功")
    
    if success_count == total_count:
        print("[OK] 所有依赖都已正确安装！")
    else:
        print("[ERROR] 部分依赖安装失败，请检查错误信息")
