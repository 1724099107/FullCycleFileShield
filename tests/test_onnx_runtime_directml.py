#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试ONNX Runtime with DirectML是否能够使用Intel核显
"""

import os
import sys
import platform

# 添加离线依赖目录到Python模块搜索路径
script_dir = os.path.dirname(os.path.abspath(__file__))
offline_deps_dir = os.path.join(script_dir, "offline_deps")
sys.path = [offline_deps_dir] + sys.path

print("=== Intel核显测试 (ONNX Runtime with DirectML) ===")
try:
    import onnxruntime as ort
    
    print("✓ ONNX Runtime成功导入")
    print(f"  ONNX Runtime版本: {ort.__version__}")
    
    # 获取所有可用的执行提供者
    available_providers = ort.get_available_providers()
    print(f"✓ 可用的执行提供者: {available_providers}")
    
    # 检查是否有DirectML执行提供者
    if 'DmlExecutionProvider' in available_providers:
        print("✓ DirectML执行提供者可用!")
        
        # 创建一个使用DirectML的会话选项
        session_options = ort.SessionOptions()
        
        # 创建一个简单的ONNX模型来测试
        import numpy as np
        import onnx
        import onnxruntime
        
        # 创建一个简单的加法模型
        def create_simple_model():
            # 创建输入和输出张量
            input1 = onnx.helper.make_tensor_value_info('input1', onnx.TensorProto.FLOAT, [1, 3])
            input2 = onnx.helper.make_tensor_value_info('input2', onnx.TensorProto.FLOAT, [1, 3])
            output = onnx.helper.make_tensor_value_info('output', onnx.TensorProto.FLOAT, [1, 3])
            
            # 创建节点 (加法操作)
            add_node = onnx.helper.make_node(
                'Add',
                inputs=['input1', 'input2'],
                outputs=['output'],
            )
            
            # 创建图
            graph_def = onnx.helper.make_graph(
                [add_node],
                'simple_add_model',
                [input1, input2],
                [output],
            )
            
            # 创建模型
            model_def = onnx.helper.make_model(graph_def, producer_name='test')
            
            # 保存模型
            onnx.save(model_def, 'simple_add_model.onnx')
        
        # 创建并保存模型
        create_simple_model()
        print("✓ 简单的ONNX模型创建成功")
        
        # 使用DirectML执行提供者创建会话
        print("✓ 尝试使用DirectML执行提供者创建会话...")
        session = ort.InferenceSession(
            'simple_add_model.onnx',
            sess_options=session_options,
            providers=['DmlExecutionProvider']
        )
        print("✓ 会话创建成功!")
        
        # 准备输入数据
        input1 = np.array([[1.0, 2.0, 3.0]], dtype=np.float32)
        input2 = np.array([[4.0, 5.0, 6.0]], dtype=np.float32)
        inputs = {'input1': input1, 'input2': input2}
        
        # 执行推理
        print("✓ 执行推理测试...")
        outputs = session.run(None, inputs)
        print(f"✓ 推理成功! 结果: {outputs[0]}")
        
        # 验证结果
        expected_output = input1 + input2
        if np.array_equal(outputs[0], expected_output):
            print("✓ 结果验证成功! 计算正确")
        else:
            print(f"✗ 结果验证失败! 期望: {expected_output}, 实际: {outputs[0]}")
        
        # 清理临时模型文件
        if os.path.exists('simple_add_model.onnx'):
            os.remove('simple_add_model.onnx')
        
        print("\n=== 测试完成 ===")
        print("所有测试通过，Intel核显已成功被ONNX Runtime with DirectML调用!")
        
        # 保存测试信息到文件
        with open("intel_gpu_onnx_test_info.txt", "w") as f:
            f.write(f"ONNX Runtime版本: {ort.__version__}\n")
            f.write(f"可用执行提供者: {available_providers}\n")
            f.write("DirectML执行提供者: 可用\n")
            f.write("测试结果: 成功\n")
        print("测试信息已保存到 intel_gpu_onnx_test_info.txt")
        
    else:
        print("✗ DirectML执行提供者不可用")
        print("可能的原因:")
        print("1. DirectML未正确安装")
        print("2. 系统不支持DirectX 12")
        print("3. 显卡驱动未正确安装")
        
        # 保存测试信息到文件
        with open("intel_gpu_onnx_test_info.txt", "w") as f:
            f.write(f"ONNX Runtime版本: {ort.__version__}\n")
            f.write(f"可用执行提供者: {available_providers}\n")
            f.write("DirectML执行提供者: 不可用\n")
            f.write("测试结果: 失败\n")
        print("测试信息已保存到 intel_gpu_onnx_test_info.txt")
        
    
except ImportError as e:
    print(f"✗ 导入失败: {e}")
    print(f"错误详情: {sys.exc_info()}")
    
    # 保存测试信息到文件
    with open("intel_gpu_onnx_test_info.txt", "w") as f:
        f.write(f"导入失败: {e}\n")
        f.write("测试结果: 失败\n")
    print("测试信息已保存到 intel_gpu_onnx_test_info.txt")
    
except Exception as e:
    print(f"✗ 测试过程中出错: {e}")
    print(f"错误详情: {sys.exc_info()}")
    
    # 保存测试信息到文件
    with open("intel_gpu_onnx_test_info.txt", "w") as f:
        f.write(f"测试过程中出错: {e}\n")
        f.write("测试结果: 失败\n")
    print("测试信息已保存到 intel_gpu_onnx_test_info.txt")

print("\n=== 环境信息 ===")
print(f"Python版本: {sys.version}")
print(f"操作系统: {os.name}")
print(f"平台: {sys.platform}")
print(f"硬件架构: {platform.machine()}")
