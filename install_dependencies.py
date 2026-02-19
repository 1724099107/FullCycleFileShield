#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FullCycleFileShield (FCFS) 依赖安装脚本

此脚本用于下载、安装所有依赖，并在安装完成后删除安装包，确保程序可以正常调用这些依赖。

注意：此脚本只下载和安装与CPU环境兼容的软件包，不包含任何GPU相关的依赖。
"""

import os
import sys
import subprocess
import platform
import datetime
from typing import List, Dict, Optional


def get_python_version() -> tuple:
    """
    获取当前Python版本
    
    Returns:
        tuple: Python版本号元组
    """
    return tuple(map(int, platform.python_version().split('.')))


def read_requirements(requirements_file: str) -> List[str]:
    """
    从requirements.txt文件读取依赖列表
    
    Args:
        requirements_file: requirements.txt文件路径
        
    Returns:
        List[str]: 依赖包列表
    """
    try:
        with open(requirements_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        dependencies = []
        for line in lines:
            line = line.strip()
            # 跳过注释和空行
            if line and not line.startswith('#'):
                dependencies.append(line)
        
        return dependencies
    except Exception as e:
        print(f"读取requirements.txt文件失败: {e}")
        return []


def download_dependency(dependency: str, download_dir: str) -> bool:
    """
    下载单个依赖到本地目录
    
    Args:
        dependency: 依赖包名称及版本
        download_dir: 下载目录
        
    Returns:
        bool: 下载是否成功
    """
    try:
        print(f"正在下载依赖: {dependency}")
        
        # 清理已存在的文件，确保直接替换
        if os.path.exists(download_dir):
            # 获取依赖包名称（不含版本号）
            package_name = dependency
            if '==' in package_name:
                package_name = package_name.split('==')[0]
            elif '>=' in package_name:
                package_name = package_name.split('>=')[0]
            elif '<=' in package_name:
                package_name = package_name.split('<=')[0]
            package_name = package_name.strip()
            
            # 删除已存在的相关文件
            for file in os.listdir(download_dir):
                if file.startswith(package_name) and (file.endswith('.whl') or file.endswith('.tar.gz')):
                    file_path = os.path.join(download_dir, file)
                    os.remove(file_path)
                    print(f"已删除已存在的文件: {file}")
        
        # 构建pip命令
        pip_cmd = [
            sys.executable,
            '-m', 'pip',
            'download',
            '--dest', download_dir,
            '--no-cache-dir',
            dependency
        ]
        
        # 执行pip命令
        result = subprocess.run(
            pip_cmd,
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.returncode == 0:
            print(f"✓ 依赖下载成功: {dependency}")
            return True
        else:
            print(f"✗ 依赖下载失败: {dependency}")
            print(f"错误信息: {result.stderr}")
            return False
    except Exception as e:
        print(f"下载依赖时出错: {dependency} - {e}")
        return False


def install_dependency(package_path: str) -> bool:
    """
    安装单个依赖包
    
    Args:
        package_path: 依赖包文件路径
        
    Returns:
        bool: 安装是否成功
    """
    try:
        print(f"正在安装依赖: {os.path.basename(package_path)}")
        
        # 构建pip命令
        pip_cmd = [
            sys.executable,
            '-m', 'pip',
            'install',
            '--no-cache-dir',
            package_path
        ]
        
        # 执行pip命令
        result = subprocess.run(
            pip_cmd,
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.returncode == 0:
            print(f"✓ 依赖安装成功: {os.path.basename(package_path)}")
            return True
        else:
            print(f"✗ 依赖安装失败: {os.path.basename(package_path)}")
            print(f"错误信息: {result.stderr}")
            return False
    except Exception as e:
        print(f"安装依赖时出错: {package_path} - {e}")
        return False


def clean_up_installation_files(download_dir: str) -> None:
    """
    清理安装文件
    
    Args:
        download_dir: 下载目录
    """
    try:
        print(f"正在清理安装文件...")
        
        if os.path.exists(download_dir):
            # 获取下载目录中的所有文件
            files = os.listdir(download_dir)
            
            # 删除所有whl和tar.gz文件
            deleted_count = 0
            for file in files:
                if file.endswith('.whl') or file.endswith('.tar.gz'):
                    file_path = os.path.join(download_dir, file)
                    os.remove(file_path)
                    deleted_count += 1
                    print(f"已删除安装文件: {file}")
            
            print(f"清理完成，共删除 {deleted_count} 个文件")
        else:
            print(f"下载目录不存在: {download_dir}")
    except Exception as e:
        print(f"清理安装文件时出错: {e}")


def verify_dependencies() -> bool:
    """
    验证依赖是否正确安装
    
    Returns:
        bool: 所有核心依赖是否都已安装
    """
    print("\n=== 依赖验证 ===")
    
    # 核心依赖列表
    core_dependencies = [
        ("Cryptodome", "pycryptodomex", True),  # 加密核心，必须
        ("py7zr", "py7zr", True),              # 压缩功能，必须
        ("psutil", "psutil", False),            # 系统监控，可选
        ("PyQt5", "PyQt5", True),              # GUI，必须
        ("numpy", "numpy", False),              # 数值计算，可选
    ]
    
    # Windows系统特有依赖
    if platform.system() == "Windows":
        core_dependencies.append(("win32file", "pywin32", False))  # 文件元数据删除，可选
    
    all_core_ok = True
    missing_optional = []
    
    for import_name, package_name, is_core in core_dependencies:
        try:
            module = __import__(import_name)
            version = getattr(module, "__version__", "未知版本")
            print(f"[OK] {import_name} 已安装 (版本: {version})")
        except ImportError as e:
            print(f"[ERROR] 无法导入 {import_name}: {e}")
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


def main():
    """
    主函数
    """
    print("=== FullCycleFileShield 依赖安装脚本 ===")
    print(f"执行时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Python版本: {platform.python_version()}")
    print(f"操作系统: {platform.platform()}")
    print()
    
    # 检查Python版本
    python_version = get_python_version()
    if python_version < (3, 12):
        print("警告: Python版本低于推荐的3.12")
        print("某些依赖可能无法正常工作，请考虑升级Python版本。")
        print()
    
    # 定义路径
    script_dir = os.path.dirname(os.path.abspath(__file__))
    requirements_file = os.path.join(script_dir, 'requirements.txt')
    download_dir = os.path.join(script_dir, 'offline_deps')
    
    print(f"脚本所在目录: {script_dir}")
    print(f"requirements.txt文件: {requirements_file}")
    print(f"依赖下载目录: {download_dir}")
    print()
    
    # 检查requirements.txt文件是否存在
    if not os.path.exists(requirements_file):
        print(f"错误: requirements.txt文件不存在于 {requirements_file}")
        sys.exit(1)
    
    # 读取依赖列表
    dependencies = read_requirements(requirements_file)
    
    if not dependencies:
        print("错误: 未找到依赖列表或依赖列表为空")
        sys.exit(1)
    
    # 创建下载目录（如果不存在）
    os.makedirs(download_dir, exist_ok=True)
    
    # 下载所有依赖
    print(f"开始下载所有依赖到目录: {download_dir}")
    print(f"总共需要下载 {len(dependencies)} 个依赖包")
    print("=" * 80)
    
    download_status = {}
    success_count = 0
    failure_count = 0
    
    for i, dependency in enumerate(dependencies, 1):
        print(f"\n[{i}/{len(dependencies)}]")
        if download_dependency(dependency, download_dir):
            download_status[dependency] = True
            success_count += 1
        else:
            download_status[dependency] = False
            failure_count += 1
    
    print("=" * 80)
    print(f"依赖下载完成！")
    print(f"成功: {success_count}")
    print(f"失败: {failure_count}")
    print()
    
    # 安装所有依赖
    print("开始安装所有依赖...")
    print("=" * 80)
    
    install_status = {}
    install_success_count = 0
    install_failure_count = 0
    
    # 获取下载的文件
    if os.path.exists(download_dir):
        downloaded_files = [f for f in os.listdir(download_dir) if f.endswith('.whl') or f.endswith('.tar.gz')]
        
        for i, file_name in enumerate(downloaded_files, 1):
            print(f"\n[{i}/{len(downloaded_files)}]")
            file_path = os.path.join(download_dir, file_name)
            if install_dependency(file_path):
                install_status[file_name] = True
                install_success_count += 1
            else:
                install_status[file_name] = False
                install_failure_count += 1
    
    print("=" * 80)
    print(f"依赖安装完成！")
    print(f"成功: {install_success_count}")
    print(f"失败: {install_failure_count}")
    print()
    
    # 清理安装文件
    clean_up_installation_files(download_dir)
    print()
    
    # 验证依赖
    print("验证依赖是否正确安装...")
    verification_success = verify_dependencies()
    print()
    
    # 总结
    print("=== 安装总结 ===")
    print(f"依赖包总数: {len(dependencies)}")
    print(f"成功下载: {success_count}")
    print(f"失败下载: {failure_count}")
    print(f"成功安装: {install_success_count}")
    print(f"失败安装: {install_failure_count}")
    print(f"依赖验证: {'成功' if verification_success else '失败'}")
    print()
    
    if failure_count > 0 or install_failure_count > 0 or not verification_success:
        print("警告: 部分依赖安装失败，可能会影响程序的正常运行。")
        print("请检查网络连接和依赖包名称是否正确。")
        sys.exit(1)
    else:
        print("✓ 所有依赖安装成功！")
        print("现在您可以运行 start_fcfs.py 来启动程序。")
        print()
        print("如果程序无法正常启动，请尝试以下步骤:")
        print("1. 确保您的Python版本为3.12或更高")
        print("2. 尝试使用pip直接安装依赖: pip install -r requirements.txt")
        sys.exit(0)


if __name__ == "__main__":
    main()
