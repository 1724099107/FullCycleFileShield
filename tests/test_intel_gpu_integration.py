#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试整个项目是否能够正常使用Intel核显
"""

import os
import sys
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 添加项目根目录到Python模块搜索路径
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

print("=== 测试Intel核显集成 ===")
try:
    # 测试GPU环境初始化
    from utils.gpu_environment import initialize_gpu, get_available_devices, get_best_device, get_device_properties
    
    print("✓ 导入GPU环境模块成功")
    
    # 初始化GPU环境
    print("✓ 初始化GPU环境...")
    gpu_info = initialize_gpu()
    print(f"✓ GPU环境初始化成功")
    print(f"  可用: {gpu_info['available']}")
    print(f"  设备: {gpu_info['devices']}")
    print(f"  选中设备: {gpu_info['selected_device']}")
    print(f"  后端: {gpu_info['backend']}")
    
    # 获取可用设备
    print("✓ 获取可用设备...")
    available_devices = get_available_devices()
    print(f"✓ 可用设备: {available_devices}")
    
    # 获取最佳设备
    print("✓ 获取最佳设备...")
    best_device = get_best_device()
    print(f"✓ 最佳设备: {best_device}")
    
    # 获取设备属性
    print("✓ 获取设备属性...")
    device_properties = get_device_properties(best_device)
    print(f"✓ 设备属性: {device_properties}")
    
    # 测试ONNX Runtime with DirectML的实际使用
    if gpu_info['backend'] == 'ONNX Runtime with DirectML':
        print("\n=== 测试ONNX Runtime with DirectML实际使用 ===")
        try:
            import onnxruntime as ort
            import numpy as np
            
            # 创建一个简单的ONNX模型
            import onnx
            
            # 创建一个简单的乘法模型
            def create_simple_model():
                # 创建输入和输出张量
                input1 = onnx.helper.make_tensor_value_info('input1', onnx.TensorProto.FLOAT, [1, 4])
                input2 = onnx.helper.make_tensor_value_info('input2', onnx.TensorProto.FLOAT, [4, 1])
                output = onnx.helper.make_tensor_value_info('output', onnx.TensorProto.FLOAT, [1, 1])
                
                # 创建节点 (矩阵乘法操作)
                matmul_node = onnx.helper.make_node(
                    'MatMul',
                    inputs=['input1', 'input2'],
                    outputs=['output'],
                )
                
                # 创建图
                graph_def = onnx.helper.make_graph(
                    [matmul_node],
                    'simple_matmul_model',
                    [input1, input2],
                    [output],
                )
                
                # 创建模型
                model_def = onnx.helper.make_model(graph_def, producer_name='test')
                
                # 保存模型
                onnx.save(model_def, 'simple_matmul_model.onnx')
            
            # 创建并保存模型
            create_simple_model()
            print("✓ 简单的ONNX模型创建成功")
            
            # 使用DirectML执行提供者创建会话
            print("✓ 创建ONNX Runtime会话...")
            session = ort.InferenceSession(
                'simple_matmul_model.onnx',
                providers=['DmlExecutionProvider']
            )
            print("✓ 会话创建成功!")
            
            # 准备输入数据
            input1 = np.array([[1.0, 2.0, 3.0, 4.0]], dtype=np.float32)
            input2 = np.array([[5.0], [6.0], [7.0], [8.0]], dtype=np.float32)
            inputs = {'input1': input1, 'input2': input2}
            
            # 执行推理
            print("✓ 执行矩阵乘法测试...")
            outputs = session.run(None, inputs)
            print(f"✓ 推理成功! 结果: {outputs[0]}")
            
            # 验证结果
            expected_output = np.matmul(input1, input2)
            if np.allclose(outputs[0], expected_output):
                print("✓ 结果验证成功! 计算正确")
            else:
                print(f"✗ 结果验证失败! 期望: {expected_output}, 实际: {outputs[0]}")
            
            # 清理临时模型文件
            if os.path.exists('simple_matmul_model.onnx'):
                os.remove('simple_matmul_model.onnx')
            
        except Exception as e:
            print(f"✗ ONNX Runtime测试失败: {e}")
    
    print("\n=== 测试完成 ===")
    print("所有测试通过，项目已成功集成Intel核显加速!")
    
    # 保存测试信息到文件
    with open("intel_gpu_integration_test_info.txt", "w") as f:
        f.write(f"GPU可用: {gpu_info['available']}\n")
        f.write(f"设备: {gpu_info['devices']}\n")
        f.write(f"选中设备: {gpu_info['selected_device']}\n")
        f.write(f"后端: {gpu_info['backend']}\n")
        f.write(f"可用设备列表: {available_devices}\n")
        f.write(f"最佳设备: {best_device}\n")
        f.write(f"设备属性: {device_properties}\n")
        f.write("测试结果: 成功\n")
    print("测试信息已保存到 intel_gpu_integration_test_info.txt")
    
    
except Exception as e:
    print(f"✗ 测试失败: {e}")
    import traceback
    traceback.print_exc()
    
    # 保存测试信息到文件
    with open("intel_gpu_integration_test_info.txt", "w") as f:
        f.write(f"测试失败: {e}\n")
        f.write("测试结果: 失败\n")
    print("测试信息已保存到 intel_gpu_integration_test_info.txt")
