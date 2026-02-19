#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FullCycleFileShield (FCFS) 依赖下载脚本

此脚本用于在第一次运行前下载所有依赖到本地目录，确保程序可以正常调用这些依赖。
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


def download_all_dependencies(dependencies: List[str], download_dir: str) -> Dict[str, bool]:
    """
    下载所有依赖到本地目录
    
    Args:
        dependencies: 依赖包列表
        download_dir: 下载目录
        
    Returns:
        Dict[str, bool]: 依赖下载状态字典
    """
    print(f"开始下载所有依赖到目录: {download_dir}")
    print(f"总共需要下载 {len(dependencies)} 个依赖包")
    print("=" * 80)
    
    # 创建下载目录（如果不存在）
    os.makedirs(download_dir, exist_ok=True)
    
    # 下载所有依赖
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
    
    return download_status


def verify_download(download_dir: str) -> List[str]:
    """
    验证下载的依赖包
    
    Args:
        download_dir: 下载目录
        
    Returns:
        List[str]: 下载的依赖包列表
    """
    try:
        print(f"\n验证下载的依赖包...")
        
        # 获取下载目录中的所有文件
        files = os.listdir(download_dir)
        
        # 过滤出whl和tar.gz文件
        deps_files = [f for f in files if f.endswith('.whl') or f.endswith('.tar.gz')]
        
        print(f"在目录 {download_dir} 中找到 {len(deps_files)} 个依赖包文件")
        
        if deps_files:
            print("下载的依赖包:")
            for dep_file in deps_files[:10]:  # 只显示前10个
                print(f"  - {dep_file}")
            
            if len(deps_files) > 10:
                print(f"  ... 等 {len(deps_files) - 10} 个文件")
        
        return deps_files
    except Exception as e:
        print(f"验证下载的依赖包时出错: {e}")
        return []


def main():
    """
    主函数
    """
    print("=== FullCycleFileShield 依赖下载脚本 ===")
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
    
    # 下载所有依赖
    download_status = download_all_dependencies(dependencies, download_dir)
    
    # 验证下载
    downloaded_files = verify_download(download_dir)
    
    # 总结
    print("\n=== 下载总结 ===")
    print(f"依赖包总数: {len(dependencies)}")
    print(f"成功下载: {sum(1 for status in download_status.values() if status)}")
    print(f"失败下载: {sum(1 for status in download_status.values() if not status)}")
    print(f"下载的文件数: {len(downloaded_files)}")
    print()
    
    if sum(1 for status in download_status.values() if not status) > 0:
        print("警告: 部分依赖下载失败，可能会影响程序的正常运行。")
        print("请检查网络连接和依赖包名称是否正确。")
        sys.exit(1)
    else:
        print("✓ 所有依赖下载成功！")
        print("现在您可以运行 start_fcfs.py 来启动程序，它会使用本地下载的依赖。")
        print()
        print("如果程序无法正常启动，请尝试以下步骤:")
        print("1. 确保您的Python版本为3.12或更高")
        print("2. 确保offline_deps目录存在且包含所有必要的依赖")
        print("3. 尝试使用pip直接安装依赖: pip install -r requirements.txt")
        sys.exit(0)


if __name__ == "__main__":
    main()