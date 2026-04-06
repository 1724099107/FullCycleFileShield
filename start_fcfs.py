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
    
    # 检查是否为Windows系统
    if not platform.system() == "Windows":
        print("[警告] 本软件仅支持Windows系统，可能无法正常运行！")
    
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

def show_usage():
    """
    显示使用说明
    """
    print("""
=== FullCycleFileShield 使用说明 ===

启动模式:
  1. 图形界面模式 (默认)
     命令: python start_fcfs.py
     或:   python start_fcfs.py gui

  2. 命令行模式 (CLI)
     命令: python start_fcfs.py cli [子命令]
     
     子命令:
       encrypt   加密文件或文件夹
       decrypt   解密加密包
       delete    彻底删除文件或文件夹
       
     示例:
       python start_fcfs.py cli encrypt -i file.txt
       python start_fcfs.py cli decrypt -i package.7z.enc
       python start_fcfs.py cli delete -f file.txt
       
     帮助:
       python start_fcfs.py cli --help
       python start_fcfs.py cli encrypt --help

更多信息:
  请查看 README.md 或项目文档
=====================================
""")


def run_cli_mode(cli_args):
    """
    运行CLI模式
    
    Args:
        cli_args: CLI参数列表
    """
    try:
        from cli.main import CLI
        cli = CLI()
        
        # 如果有命令行参数，直接执行
        if cli_args:
            return cli.run(cli_args)
        else:
            # 进入交互式命令输入循环
            print("\n=== FullCycleFileShield 命令行模式 ===")
            print("输入 'help' 查看可用命令")
            print("输入 'exit' 退出程序")
            print("====================================")
            
            while True:
                try:
                    # 显示命令提示符
                    user_input = input("fcfs> ").strip()
                    
                    # 处理特殊命令
                    if not user_input:
                        continue
                    elif user_input.lower() == 'exit':
                        print("退出命令行模式...")
                        return 0
                    elif user_input.lower() == 'help':
                        # 显示帮助信息
                        cli.parser.print_help()
                        continue
                    
                    # 解析用户输入并执行命令
                    args = user_input.split()
                    exit_code = cli.run(args)
                    
                    # 如果命令执行失败，继续循环
                    if exit_code != 0:
                        print("")
                        continue
                        
                except KeyboardInterrupt:
                    print("\n按下Ctrl+C，退出命令行模式...")
                    return 0
                except EOFError:
                    print("\n退出命令行模式...")
                    return 0
                except Exception as e:
                    print(f"命令执行出错: {str(e)}")
                    print("\n")
                    continue
                    
    except ImportError as e:
        print(f"[ERROR] 无法启动CLI模式: {e}")
        print("请确保CLI模块已正确安装")
        return 1
    except Exception as e:
        print(f"[ERROR] CLI模式运行失败: {e}")
        return 1


def run_gui_mode():
    """
    运行GUI模式
    """
    try:
        from gui.main_window import MainWindow
        from PyQt5.QtWidgets import QApplication
        
        app = QApplication(sys.argv)
        window = MainWindow()
        return app.exec_()
    except ImportError as e:
        print(f"\n[ERROR] 导入主程序模块失败: {e}")
        write_error_log("导入主程序模块失败", e)
        print("\n按任意键退出...")
        try:
            input()
        except:
            pass
        return 1
    except Exception as e:
        print(f"\n[ERROR] 启动主程序失败: {e}")
        write_error_log("启动主程序失败", e)
        raise


if __name__ == "__main__":
    try:
        # 检查是否为Windows系统
        if not platform.system() == "Windows":
            print("[错误] 本软件仅支持Windows系统，无法在当前操作系统上运行！")
            print(f"当前操作系统: {platform.platform()}")
            print("请在Windows 10/11系统上运行本软件。")
            print("\n按任意键退出...")
            try:
                input()
            except:
                pass
            sys.exit(1)
        
        # 解析命令行参数
        if len(sys.argv) > 1:
            if sys.argv[1] in ('--help', '-h', 'help'):
                show_usage()
                sys.exit(0)
            elif sys.argv[1] == 'cli':
                # CLI模式
                # 清除旧的错误日志
                try:
                    if os.path.exists(log_file):
                        os.remove(log_file)
                except:
                    pass
                
                # 检查依赖
                if not check_dependencies():
                    print("\n[ERROR] 核心依赖检查失败")
                    sys.exit(1)
                
                # 运行CLI
                cli_args = sys.argv[2:] if len(sys.argv) > 2 else []
                exit_code = run_cli_mode(cli_args)
                sys.exit(exit_code)
            elif sys.argv[1] == 'gui':
                # GUI模式（显式指定）
                mode = 'gui'
            else:
                print(f"[错误] 未知参数: {sys.argv[1]}")
                show_usage()
                sys.exit(1)
        else:
            # 让用户选择模式
            print("\n=== 模式选择 ===")
            print("请选择启动模式：")
            print("1. 图形界面模式 (GUI)")
            print("2. 命令行模式 (CLI)")
            print()
            
            while True:
                choice = input("请输入数字 (1-2): ").strip()
                if choice == '1':
                    mode = 'gui'
                    break
                elif choice == '2':
                    mode = 'cli'
                    break
                else:
                    print("输入错误，请重新输入！")
        
        # 清除旧的错误日志
        try:
            if os.path.exists(log_file):
                os.remove(log_file)
        except:
            pass
        
        # 检查是否是首次启动
        first_run_flag = os.path.join(script_dir, ".first_run")
        if not os.path.exists(first_run_flag):
            print("\n=== 温馨提示 ===")
            print("欢迎使用 FullCycleFileShield (FCFS)！")
            print("这是您首次启动FCFS，建议您先安装所有必要的依赖。")
            print("\n安装依赖的方法：")
            print("直接安装依赖：python -m pip install -r requirements.txt")
            print("\n依赖安装完成后，FCFS将能够正常运行所有功能。")
            print("==================\n")
            
            # 创建首次启动标记文件
            try:
                with open(first_run_flag, "w") as f:
                    f.write(f"First run: {datetime.datetime.now().isoformat()}")
            except Exception:
                pass
        
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
        
        # 根据选择启动相应模式
        if mode == 'gui':
            # 启动GUI模式
            exit_code = run_gui_mode()
            sys.exit(exit_code)
        elif mode == 'cli':
            # 启动CLI模式
            cli_args = sys.argv[2:] if len(sys.argv) > 2 else []
            exit_code = run_cli_mode(cli_args)
            sys.exit(exit_code)
        
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
