#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
依赖验证和目录结构检查模块
负责检查项目的依赖项和目录结构
"""

import os
import sys
import importlib
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_dependencies(dependencies=None):
    """
    检查项目的依赖项
    
    Args:
        dependencies (list): 要检查的依赖项列表
    
    Returns:
        dict: 依赖项检查结果
    """
    if dependencies is None:
        # 默认检查的依赖项
        dependencies = [
            'PyQt5',
            'pycryptodomex',
            'py7zr',
            'psutil',
            'numpy'
        ]
    
    check_results = {}
    
    for dependency in dependencies:
        try:
            importlib.import_module(dependency)
            check_results[dependency] = {
                'available': True,
                'error': None
            }
            logger.info(f"依赖项 {dependency} 可用")
        except ImportError as e:
            check_results[dependency] = {
                'available': False,
                'error': str(e)
            }
            logger.warning(f"依赖项 {dependency} 不可用: {e}")
    
    return check_results

def check_directory_structure(base_path=None):
    """
    检查项目的目录结构
    
    Args:
        base_path (str): 项目的基础路径
    
    Returns:
        dict: 目录结构检查结果
    """
    if base_path is None:
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # 预期的目录结构
    expected_structure = {
        'config': ['settings.json', 'settings.py'],
        'decryption': ['cleanup.py', 'pre_check.py', 'decompression.py', 'hybrid_decryption.py'],
        'deletion': ['bmb21_2019.py', 'verification.py'],
        'encryption': ['cleanup.py', 'compression.py', 'pre_check.py', 'quantum_key.py', 'hybrid_encryption.py', 'anti_quantum_alg.py'],
        'feedback': [],
        'gui': ['about_tab.py', 'decryption_tab.py', 'deletion_tab.py', 'encryption_tab.py', 'main_window.py', 'system_tray.py'],
        'lib': [],
        'tests': [],
        'tmp': [],
        'utils': ['__init__.py', 'gpu_environment.py', 'memory_cleaner.py', 'hash_calculator.py', 'dependency_checker.py']
    }
    
    # 预期的根目录文件
    expected_root_files = [
        'LICENSE',
        'README.md',
        'offline_maintenance.py',
        'start_fcfs.py',
        'run_fcfs.bat'
    ]
    
    structure_results = {
        'directories': {},
        'root_files': {},
        'missing_directories': [],
        'missing_files': []
    }
    
    # 检查目录结构
    for directory, expected_files in expected_structure.items():
        directory_path = os.path.join(base_path, directory)
        if os.path.exists(directory_path) and os.path.isdir(directory_path):
            structure_results['directories'][directory] = {
                'exists': True,
                'files': {}
            }
            
            # 检查目录中的文件
            for file_name in expected_files:
                file_path = os.path.join(directory_path, file_name)
                if os.path.exists(file_path) and os.path.isfile(file_path):
                    structure_results['directories'][directory]['files'][file_name] = {
                        'exists': True
                    }
                else:
                    structure_results['directories'][directory]['files'][file_name] = {
                        'exists': False
                    }
                    structure_results['missing_files'].append(os.path.join(directory, file_name))
        else:
            structure_results['directories'][directory] = {
                'exists': False
            }
            structure_results['missing_directories'].append(directory)
    
    # 检查根目录文件
    for file_name in expected_root_files:
        file_path = os.path.join(base_path, file_name)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            structure_results['root_files'][file_name] = {
                'exists': True
            }
        else:
            structure_results['root_files'][file_name] = {
                'exists': False
            }
            structure_results['missing_files'].append(file_name)
    
    # 记录检查结果
    logger.info(f"目录结构检查完成")
    logger.info(f"缺失的目录: {structure_results['missing_directories']}")
    logger.info(f"缺失的文件: {structure_results['missing_files']}")
    
    return structure_results

def check_python_version(min_version=(3, 9)):
    """
    检查Python版本
    
    Args:
        min_version (tuple): 最小要求的Python版本
    
    Returns:
        dict: Python版本检查结果
    """
    current_version = sys.version_info
    is_compatible = current_version >= min_version
    
    result = {
        'current_version': f"{current_version.major}.{current_version.minor}.{current_version.micro}",
        'min_version': f"{min_version[0]}.{min_version[1]}",
        'is_compatible': is_compatible
    }
    
    if is_compatible:
        logger.info(f"Python版本 {result['current_version']} 符合要求")
    else:
        logger.warning(f"Python版本 {result['current_version']} 不符合要求，至少需要 {result['min_version']}")
    
    return result

def check_system_environment():
    """
    检查系统环境
    
    Returns:
        dict: 系统环境检查结果
    """
    import platform
    
    system_info = {
        'os': platform.system(),
        'os_version': platform.version(),
        'architecture': platform.architecture(),
        'machine': platform.machine(),
        'python_version': platform.python_version(),
        'python_implementation': platform.python_implementation()
    }
    
    logger.info(f"系统环境: {system_info}")
    
    return system_info

def generate_environment_report(base_path=None):
    """
    生成环境报告
    
    Args:
        base_path (str): 项目的基础路径
    
    Returns:
        dict: 环境报告
    """
    report = {
        'system': check_system_environment(),
        'python': check_python_version(),
        'dependencies': check_dependencies(),
        'structure': check_directory_structure(base_path)
    }
    
    # 检查是否所有依赖项都可用
    all_dependencies_available = all(
        result['available'] for result in report['dependencies'].values()
    )
    
    # 检查是否所有目录都存在
    all_directories_exist = all(
        result['exists'] for result in report['structure']['directories'].values()
    )
    
    # 检查是否有缺失的文件
    has_missing_files = len(report['structure']['missing_files']) > 0
    
    # 生成总体状态
    report['overall_status'] = {
        'dependencies_available': all_dependencies_available,
        'directories_exist': all_directories_exist,
        'has_missing_files': has_missing_files,
        'ready': all_dependencies_available and all_directories_exist and not has_missing_files
    }
    
    logger.info(f"环境报告生成完成，项目状态: {'就绪' if report['overall_status']['ready'] else '需要修复'}")
    
    return report

def fix_missing_structure(base_path=None):
    """
    修复缺失的目录结构
    
    Args:
        base_path (str): 项目的基础路径
    
    Returns:
        dict: 修复结果
    """
    if base_path is None:
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    structure = check_directory_structure(base_path)
    fix_results = {
        'created_directories': [],
        'created_files': []
    }
    
    # 创建缺失的目录
    for directory in structure['missing_directories']:
        directory_path = os.path.join(base_path, directory)
        try:
            os.makedirs(directory_path, exist_ok=True)
            fix_results['created_directories'].append(directory)
            logger.info(f"创建目录: {directory}")
        except Exception as e:
            logger.error(f"创建目录 {directory} 时出错: {e}")
    
    logger.info(f"目录结构修复完成")
    
    return fix_results

def check_dependency(dependency_name, extra_info=None):
    """
    检查单个依赖项并返回导入的模块
    
    Args:
        dependency_name (str): 依赖项名称
        extra_info (str, optional): 额外信息
    
    Returns:
        module: 导入的模块
    """
    try:
        module = importlib.import_module(dependency_name)
        logger.info(f"依赖项 {dependency_name} 可用" + (f" ({extra_info})" if extra_info else ""))
        return module
    except ImportError as e:
        error_message = f"依赖项 {dependency_name} 不可用" + (f" ({extra_info})" if extra_info else "")
        logger.error(f"{error_message}: {e}")
        raise ImportError(error_message) from e

if __name__ == "__main__":
    # 生成环境报告
    print("生成环境报告...")
    report = generate_environment_report()
    
    # 打印报告摘要
    print("\n=== 环境报告摘要 ===")
    print(f"系统: {report['system']['os']} {report['system']['os_version']}")
    print(f"架构: {report['system']['machine']} {report['system']['architecture'][0]}")
    print(f"Python版本: {report['python']['current_version']} ({'符合要求' if report['python']['is_compatible'] else '不符合要求'})")
    
    print("\n依赖项状态:")
    for dependency, status in report['dependencies'].items():
        print(f"  - {dependency}: {'可用' if status['available'] else '不可用'}")
    
    print("\n目录结构状态:")
    print(f"  缺失的目录: {report['structure']['missing_directories']}")
    print(f"  缺失的文件: {report['structure']['missing_files']}")
    
    print(f"\n总体状态: {'就绪' if report['overall_status']['ready'] else '需要修复'}")
    
    # 如果需要修复，尝试修复
    if not report['overall_status']['ready']:
        if input("\n是否尝试修复目录结构? (y/n): ").lower() == 'y':
            fix_results = fix_missing_structure()
            print(f"创建的目录: {fix_results['created_directories']}")
            print(f"修复完成")
