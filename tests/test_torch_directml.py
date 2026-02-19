#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试Intel核显是否能够被PyTorch调用
"""

import os
import sys
import platform

# 添加离线依赖目录到Python模块搜索路径
script_dir = os.path.dirname(os.path.abspath(__file__))
offline_deps_dir = os.path.join(script_dir, "offline_deps")
sys.path = [offline_deps_dir] + sys.path

print("=== Intel核显测试 ===")
try:
    import torch
    import torch_directml
    
    print("✓ PyTorch成功导入")
    print(f"  PyTorch版本: {torch.__version__}")
    print(f"  Torch DirectML版本: {torch_directml.__version__}")
    
    # 获取DirectML设备
    dml_device = torch_directml.device()
    print(f"✓ DirectML设备获取成功: {dml_device}")
    
    # 测试基本功能
    print("\n=== 基本功能测试 ===")
    # 在CPU上创建张量
    x = torch.tensor([1.0, 2.0, 3.0])
    print(f"✓ CPU张量创建成功: {x}")
    
    # 将张量移到DirectML设备上
    x_dml = x.to(dml_device)
    print(f"✓ DirectML张量创建成功: {x_dml}")
    
    # 测试张量运算
    y_dml = x_dml * 2
    print(f"✓ DirectML张量运算成功: {y_dml}")
    
    # 将结果移回CPU
    y_cpu = y_dml.to("cpu")
    print(f"✓ 结果移回CPU成功: {y_cpu}")
    
    # 测试模型创建和推理
    print("\n=== 模型测试 ===")
    # 创建一个简单的线性模型
    model = torch.nn.Linear(3, 1)
    # 将模型移到DirectML设备上
    model_dml = model.to(dml_device)
    print("✓ 模型移到DirectML设备成功")
    
    # 测试模型推理
    input_tensor = torch.tensor([[1.0, 2.0, 3.0]])
    input_tensor_dml = input_tensor.to(dml_device)
    output_dml = model_dml(input_tensor_dml)
    output_cpu = output_dml.to("cpu")
    print(f"✓ 模型推理成功: {output_cpu}")
    
    print("\n=== 测试完成 ===")
    print("所有测试通过，Intel核显已成功被PyTorch调用!")
    
    # 保存测试信息到文件
    with open("intel_gpu_test_info.txt", "w") as f:
        f.write(f"PyTorch版本: {torch.__version__}\n")
        f.write(f"Torch DirectML版本: {torch_directml.__version__}\n")
        f.write(f"DirectML设备: {dml_device}\n")
        f.write("测试结果: 成功\n")
    print("测试信息已保存到 intel_gpu_test_info.txt")
    
except ImportError as e:
    print(f"✗ 导入失败: {e}")
    print(f"错误详情: {sys.exc_info()}")
    
except Exception as e:
    print(f"✗ 测试过程中出错: {e}")
    print(f"错误详情: {sys.exc_info()}")

print("\n=== 环境信息 ===")
print(f"Python版本: {sys.version}")
print(f"操作系统: {os.name}")
print(f"平台: {sys.platform}")
print(f"硬件架构: {platform.machine()}")
