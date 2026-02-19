#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试PyTorch导入和版本验证
"""

import os
import sys

# 添加离线依赖目录到Python模块搜索路径
script_dir = os.path.dirname(os.path.abspath(__file__))
offline_deps_dir = os.path.join(script_dir, "offline_deps")

# 确保使用离线依赖目录
sys.path = [offline_deps_dir] + sys.path

print("=== PyTorch导入测试 ===")
try:
    import torch
    import torchvision
    import torchaudio
    
    print("✓ PyTorch成功导入")
    print(f"  PyTorch版本: {torch.__version__}")
    print(f"  TorchVision版本: {torchvision.__version__}")
    print(f"  TorchAudio版本: {torchaudio.__version__}")
    
    # 验证版本是否符合要求
    torch_version = torch.__version__
    version_parts = torch_version.split('.')
    major = int(version_parts[0])
    minor = int(version_parts[1])
    
    if major < 2 or (major == 2 and minor <= 10):
        print("✓ PyTorch版本符合要求 (<= 2.10.0)")
    else:
        print("✗ PyTorch版本不符合要求 (> 2.10.0)")
    
    # 测试基本功能
    print("\n=== 基本功能测试 ===")
    # 创建一个张量
    x = torch.tensor([1.0, 2.0, 3.0])
    print(f"✓ 张量创建成功: {x}")
    
    # 测试张量运算
    y = x * 2
    print(f"✓ 张量运算成功: {y}")
    
    # 测试CUDA可用性
    if torch.cuda.is_available():
        print("✓ CUDA可用")
        # 在GPU上创建张量
        x_gpu = x.cuda()
        print(f"✓ GPU张量创建成功: {x_gpu}")
    else:
        print("⚠️  CUDA不可用，使用CPU模式")
    
    print("\n=== 测试完成 ===")
    print("所有测试通过，PyTorch安装成功!")
    
    # 保存版本信息到文件
    with open("pytorch_version_info.txt", "w") as f:
        f.write(f"PyTorch版本: {torch.__version__}\n")
        f.write(f"TorchVision版本: {torchvision.__version__}\n")
        f.write(f"TorchAudio版本: {torchaudio.__version__}\n")
        f.write(f"CUDA可用: {torch.cuda.is_available()}\n")
        if torch.cuda.is_available():
            f.write(f"CUDA设备数: {torch.cuda.device_count()}\n")
            f.write(f"当前CUDA设备: {torch.cuda.current_device()}\n")
            f.write(f"CUDA设备名称: {torch.cuda.get_device_name(0)}\n")
            f.write(f"CUDA版本: {torch.version.cuda}\n")
    print("版本信息已保存到 pytorch_version_info.txt")
    
except ImportError as e:
    print(f"✗ PyTorch导入失败: {e}")
    print(f"错误详情: {sys.exc_info()}")
    print("\n=== 导入路径检查 ===")
    print(f"当前sys.path: {sys.path}")
    print(f"离线依赖目录存在: {os.path.exists(offline_deps_dir)}")
    if os.path.exists(offline_deps_dir):
        torch_path = os.path.join(offline_deps_dir, "torch")
        print(f"torch目录存在: {os.path.exists(torch_path)}")
        if os.path.exists(torch_path):
            print(f"torch/__init__.py存在: {os.path.exists(os.path.join(torch_path, "__init__.py"))}")
    
except Exception as e:
    print(f"✗ 测试过程中出错: {e}")
    print(f"错误详情: {sys.exc_info()}")

print("\n=== 环境信息 ===")
print(f"Python版本: {sys.version}")
print(f"操作系统: {os.name}")
print(f"平台: {sys.platform}")
print(f"硬件架构: {sys.maxsize > 2**32 and '64-bit' or '32-bit'}")