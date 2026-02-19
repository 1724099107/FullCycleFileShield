#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FullCycleFileShield (FCFS) 启动脚本
确保程序能够正确引用本地的依赖文件
特别优化了虚拟机环境的兼容性
"""

import os
import sys
import traceback
import datetime
import platform
from typing import Optional, Union

# 检查Python版本
required_python_version = (3, 12, 0)
current_python_version = tuple(map(int, platform.python_version().split('.')))

if current_python_version < required_python_version:
    print(f"警告: Python版本低于要求的{required_python_version[0]}.{required_python_version[1]}.{required_python_version[2]}")
    print(f"当前Python版本: {platform.python_version()}")
    print("某些功能可能无法正常工作，请考虑升级Python版本。")
    print()

# 添加本地依赖目录到Python模块搜索路径
script_dir = os.path.dirname(os.path.abspath(__file__))
lib_dir = os.path.join(script_dir, "lib")
offline_deps_dir = os.path.join(script_dir, "offline_deps")

# 保留原始sys.path，确保能够从系统的site-packages目录加载依赖包
print("保留原始sys.path，确保能够从系统的site-packages目录加载依赖包...")
# 保存原始sys.path以便后续使用
original_path = sys.path.copy()
# 在标准库路径前面添加我们的依赖目录（如果存在）
if os.path.exists(offline_deps_dir):
    sys.path.insert(0, offline_deps_dir)
    print(f"已添加离线依赖目录到sys.path: {offline_deps_dir}")
elif os.path.exists(lib_dir):
    sys.path.insert(0, lib_dir)
    print(f"已添加本地依赖目录到sys.path: {lib_dir}")
# 打印sys.path的前几个元素，确保包含了正确的路径
print(f"当前sys.path前5个元素: {sys.path[:5]}")
print(f"sys.path中是否包含site-packages: {'site-packages' in str(sys.path)}")

# 错误日志文件
log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tmp", "startup_error.log")

# 写入错误日志
def write_error_log(message: str, exception: Optional[Exception] = None) -> None:
    """
    写入错误日志
    
    Args:
        message: 错误信息
        exception: 异常对象（可选）
    """
    try:
        # 确保tmp目录存在
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        with open(log_file, "a", encoding="utf-8") as f:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{timestamp}] {message}\n")
            if exception:
                f.write(f"异常类型: {type(exception).__name__}\n")
                f.write(f"异常信息: {str(exception)}\n")
                f.write("堆栈跟踪:\n")
                traceback.print_exc(file=f)
            f.write("\n")
    except Exception as e:
        print(f"无法写入错误日志: {e}")

# 检测是否在虚拟机环境中
def is_virtual_machine() -> bool:
    """
    检测是否在虚拟机环境中
    
    Returns:
        bool: 是否在虚拟机环境中
    """
    try:
        # 检查系统信息
        system_info = platform.uname()
        machine = system_info.machine.lower()
        node = system_info.node.lower()
        
        # 常见虚拟机特征
        vm_indicators = [
            "virtual", "vm", "vbox", "virtualbox", "vmware", "hyper-v",
            "kvm", "qemu", "xen", "parallels", "docker", "wsl"
        ]
        
        # 检查系统信息中是否包含虚拟机特征
        for indicator in vm_indicators:
            if indicator in node or indicator in machine:
                return True
        
        # 检查环境变量
        env_vars = ["VBOX_MSI_INSTALL_PATH", "VMWARE_HOME", "HYPER-V"]
        for var in env_vars:
            if var in os.environ:
                return True
        
        return False
    except Exception:
        return False

# 打印当前状态信息
def print_status_info() -> None:
    """
    打印当前状态信息
    """
    print(f"=== FullCycleFileShield 启动信息 ===")
    print(f"启动时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"当前工作目录: {os.getcwd()}")
    print(f"脚本所在目录: {script_dir}")
    print(f"已添加依赖目录: {lib_dir}")
    print(f"Python版本: {sys.version}")
    print(f"Python可执行文件: {sys.executable}")
    print(f"操作系统: {platform.platform()}")
    print(f"机器类型: {platform.machine()}")
    
    # 检测是否在虚拟机环境中
    vm_detected = is_virtual_machine()
    print(f"虚拟机环境: {'是' if vm_detected else '否'}")
    
    print(f"错误日志文件: {log_file}")

# 尝试安装依赖
import subprocess
def install_dependency(package_name: str) -> bool:
    """
    安装依赖包
    
    Args:
        package_name: 依赖包名称
        
    Returns:
        bool: 安装是否成功
    """
    try:
        print(f"正在安装依赖: {package_name}")
        
        # 构建pip命令
        pip_cmd = [
            sys.executable,
            "-m", "pip",
            "install",
            package_name
        ]
        
        # 执行pip命令
        result = subprocess.run(
            pip_cmd,
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.returncode == 0:
            print(f"✓ 依赖安装成功: {package_name}")
            return True
        else:
            print(f"✗ 依赖安装失败: {package_name}")
            print(f"错误信息: {result.stderr}")
            return False
    except Exception as e:
        print(f"安装依赖时出错: {package_name} - {e}")
        return False

# 尝试导入关键依赖，验证依赖是否正确安装
def check_dependencies() -> bool:
    """
    检查依赖是否正确安装
    
    Returns:
        bool: 所有核心依赖是否都已安装
    """
    print("\n=== 依赖检查 ===")
    
    # 核心依赖列表
    core_dependencies = [
        ("Cryptodome", "pycryptodomex", True),  # 加密核心，必须
        ("py7zr", "py7zr", True),              # 压缩功能，必须
        ("psutil", "psutil", False),            # 系统监控，可选
        ("PyQt5", "PyQt5", True),              # GUI，必须
        ("numpy", "numpy", False),              # 数值计算，可选
    ]
    
    all_core_ok = True
    missing_optional = []
    
    # 检查offline_deps目录是否存在
    if os.path.exists(offline_deps_dir):
        print(f"\n=== 检测到离线依赖目录 ===")
        print("离线依赖目录存在，但安装脚本会自动处理依赖的安装和清理")
        print("继续检查依赖...")
    
    for import_name, package_name, is_core in core_dependencies:
        try:
            module = __import__(import_name)
            version = getattr(module, "__version__", "未知版本")
            print(f"[OK] {import_name} 已安装 (版本: {version})")
        except ImportError as e:
            print(f"[ERROR] 无法导入 {import_name}: {e}")
            write_error_log(f"无法导入 {import_name}: {e}", e)
            
            # 尝试自动安装依赖
            print(f"尝试自动安装依赖: {package_name}")
            if install_dependency(package_name):
                # 安装成功后，再次尝试导入
                try:
                    module = __import__(import_name)
                    version = getattr(module, "__version__", "未知版本")
                    print(f"[OK] {import_name} 安装并导入成功 (版本: {version})")
                except ImportError as e:
                    print(f"[ERROR] 安装后仍无法导入 {import_name}: {e}")
                    write_error_log(f"安装后仍无法导入 {import_name}: {e}", e)
                    if is_core:
                        all_core_ok = False
                    else:
                        missing_optional.append(import_name)
            else:
                if is_core:
                    all_core_ok = False
                else:
                    missing_optional.append(import_name)
    
    # 显示可选依赖缺失信息
    if missing_optional:
        print(f"\n[WARNING] 以下可选依赖缺失，但程序仍可运行:")
        for dep in missing_optional:
            print(f"  - {dep}")
    
    return all_core_ok

if __name__ == "__main__":
    try:
        # 清除旧的错误日志
        if os.path.exists(log_file):
            os.remove(log_file)
        
        print_status_info()
        
        # 检查依赖
        if not check_dependencies():
            print("\n[ERROR] 核心依赖检查失败，请检查错误信息")
            print("错误详情已写入: startup_error.log")
            print("\n按任意键退出...")
            try:
                input()
            except:
                pass
            sys.exit(1)
        
        print("\n所有核心依赖验证通过，启动主程序...")
        
        # 启动主程序
        try:
            from gui.main_window import MainWindow
            from PyQt5.QtWidgets import QApplication
            
            app = QApplication(sys.argv)
            window = MainWindow()
            sys.exit(app.exec_())
        except ImportError as e:
            print(f"\n[ERROR] 导入主程序模块失败: {e}")
            write_error_log("导入主程序模块失败", e)
            print("\n按任意键退出...")
            try:
                input()
            except:
                pass
            sys.exit(1)
        except Exception as e:
            print(f"\n[ERROR] 启动主程序失败: {e}")
            write_error_log("启动主程序失败", e)
            raise
        
    except Exception as e:
        print(f"\n[ERROR] 启动失败: {e}")
        print("错误详情已写入: startup_error.log")
        write_error_log("启动主程序失败", e)
        
        # 打印详细错误信息
        print("\n=== 详细错误信息 ===")
        traceback.print_exc()
        
        print("\n按任意键退出...")
        try:
            input()
        except:
            pass
        sys.exit(1)
