#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查系统GPU和CUDA信息
"""

import os
import sys
import platform

print("=== 系统信息 ===")
print(f"操作系统: {platform.platform()}")
print(f"Python版本: {sys.version}")
print(f"硬件架构: {platform.machine()}")

print("\n=== GPU检查 ===")
try:
    # 尝试导入torch来检查GPU
    import torch
    print("✓ 已安装PyTorch")
    print(f"  PyTorch版本: {torch.__version__}")
    
    if torch.cuda.is_available():
        print("✓ CUDA可用")
        print(f"  CUDA设备数: {torch.cuda.device_count()}")
        print(f"  当前CUDA设备: {torch.cuda.current_device()}")
        print(f"  CUDA设备名称: {torch.cuda.get_device_name(0)}")
        print(f"  CUDA版本: {torch.version.cuda}")
    else:
        print("⚠️  CUDA不可用")
        print("  可能的原因:")
        print("  1. 系统没有NVIDIA GPU")
        print("  2. NVIDIA驱动未安装或版本过低")
        print("  3. CUDA未安装")
        print("  4. 安装的是CPU版本的PyTorch")
        
        # 检查环境变量中的CUDA路径
        cuda_path = os.environ.get('CUDA_PATH')
        if cuda_path:
            print(f"  CUDA_PATH环境变量: {cuda_path}")
        else:
            print("  CUDA_PATH环境变量未设置")
            
except ImportError:
    print("✗ 未安装PyTorch")
    
# 检查NVIDIA驱动
print("\n=== NVIDIA驱动检查 ===")
try:
    # 尝试通过wmic命令检查NVIDIA驱动
    import subprocess
    result = subprocess.run(['wmic', 'path', 'win32_VideoController', 'get', 'Name,DriverVersion'], 
                         capture_output=True, text=True)
    print("视频控制器信息:")
    print(result.stdout)
    
    # 检查是否有NVIDIA相关信息
    if 'NVIDIA' in result.stdout:
        print("✓ 检测到NVIDIA显卡")
    else:
        print("⚠️  未检测到NVIDIA显卡")
        
except Exception as e:
    print(f"检查NVIDIA驱动时出错: {e}")

print("\n=== 检查完成 ===")
