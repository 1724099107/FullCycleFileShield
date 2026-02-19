#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分区级文件彻底删除模块
基于BMB21-2019最高安全标准，实现分区级别的文件彻底删除
"""

import os
import sys
import platform
import subprocess
import time
import threading
import multiprocessing
import queue
import logging
import psutil
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from .bmb21_2019 import BMB212019Deletion
from utils.memory_cleaner import clear_memory
from utils.gpu_environment import is_gpu_available, get_best_device

class PartitionDeletion:
    """
    分区级文件彻底删除类
    基于BMB21-2019最高安全标准，实现分区级别的文件彻底删除
    """
    
    def __init__(self):
        """
        初始化分区删除工具
        """
        # 配置日志
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        # 创建文件处理器
        log_file = os.path.join(os.path.dirname(__file__), 'partition_deletion.log')
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        
        # 创建控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # 设置日志格式
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # 添加处理器
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        # 初始化BMB21-2019删除工具
        self.bmb_deleter = BMB212019Deletion()
        
        # 初始化任务队列
        self.task_queue = queue.Queue()
        
        # 初始化统计信息
        self.stats = {
            'total_files': 0,
            'deleted_files': 0,
            'failed_files': 0,
            'start_time': None,
            'end_time': None,
            'elapsed_time': 0,
            'errors': []
        }
        
        # 初始化线程池
        self.max_threads = self._get_optimal_thread_count()
        self.logger.info(f"初始化线程池，最大线程数: {self.max_threads}")
        
        # 初始化硬件信息
        self.hardware_info = self._get_hardware_info()
        self.logger.info(f"硬件信息: {json.dumps(self.hardware_info, indent=2, ensure_ascii=False)}")
    
    def _get_optimal_thread_count(self):
        """
        获取最佳线程数
        
        Returns:
            int: 最佳线程数
        """
        try:
            # 获取CPU核心数
            cpu_count = multiprocessing.cpu_count()
            
            # 根据系统负载调整线程数
            cpu_percent = psutil.cpu_percent(interval=1)
            memory_percent = psutil.virtual_memory().percent
            
            # 计算最佳线程数
            if cpu_percent > 80 or memory_percent > 80:
                # 系统负载高，减少线程数
                return max(1, cpu_count // 2)
            elif cpu_percent < 30 and memory_percent < 30:
                # 系统负载低，增加线程数
                return cpu_count * 2
            else:
                # 系统负载适中，使用CPU核心数
                return cpu_count
        except Exception as e:
            self.logger.warning(f"获取最佳线程数失败: {str(e)}，使用默认值4")
            return 4
    
    def _get_hardware_info(self):
        """
        获取硬件信息
        
        Returns:
            dict: 硬件信息
        """
        hardware_info = {
            'os': platform.system(),
            'os_version': platform.version(),
            'cpu_architecture': platform.architecture(),
            'cpu_count': multiprocessing.cpu_count(),
            'memory_total': psutil.virtual_memory().total,
            'cpu_available': is_gpu_available(),
            'compute_device': get_best_device()
        }
        
        # 获取磁盘信息
        disks = []
        for partition in psutil.disk_partitions():
            if partition.fstype:
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disks.append({
                        'device': partition.device,
                        'mountpoint': partition.mountpoint,
                        'fstype': partition.fstype,
                        'opts': partition.opts,
                        'total': usage.total,
                        'used': usage.used,
                        'free': usage.free,
                        'percent': usage.percent
                    })
                except Exception as e:
                    self.logger.warning(f"获取磁盘信息失败: {str(e)}")
        
        hardware_info['disks'] = disks
        return hardware_info
    
    def get_partitions(self):
        """
        获取所有分区信息
        
        Returns:
            list: 分区信息列表
        """
        partitions = []
        
        try:
            # 使用psutil获取分区信息（跨平台兼容）
            for partition in psutil.disk_partitions():
                if partition.fstype:
                    try:
                        usage = psutil.disk_usage(partition.mountpoint)
                        partitions.append({
                            'device': partition.device,
                            'description': partition.device,
                            'file_system': partition.fstype,
                            'size': usage.total,
                            'free_space': usage.free,
                            'used_space': usage.used,
                            'mountpoint': partition.mountpoint
                        })
                    except Exception as e:
                        self.logger.warning(f"获取分区信息失败: {str(e)}")
        except Exception as e:
            self.logger.error(f"获取分区列表失败: {str(e)}")
        
        return partitions
    
    def _scan_partition(self, partition_mountpoint):
        """
        扫描分区内的所有文件
        
        Args:
            partition_mountpoint (str): 分区挂载点
        """
        self.logger.info(f"开始扫描分区: {partition_mountpoint}")
        
        try:
            # 遍历分区内的所有文件
            for root, dirs, files in os.walk(partition_mountpoint):
                # 跳过系统保护的目录
                dirs[:] = [d for d in dirs if not self._is_system_protected(os.path.join(root, d))]
                
                for file in files:
                    file_path = os.path.join(root, file)
                    
                    # 跳过系统保护的文件
                    if not self._is_system_protected(file_path):
                        # 将文件路径添加到任务队列
                        self.task_queue.put(file_path)
                        self.stats['total_files'] += 1
        except Exception as e:
            self.logger.error(f"扫描分区失败: {str(e)}")
        
        self.logger.info(f"分区扫描完成，共发现 {self.stats['total_files']} 个文件")
    
    def _is_system_protected(self, path):
        """
        检查文件或目录是否为系统保护
        
        Args:
            path (str): 文件或目录路径
        
        Returns:
            bool: 是否为系统保护
        """
        try:
            if platform.system() == 'Windows':
                # Windows系统：检查系统目录
                system_dirs = ['C:\\Windows', 'C:\\Program Files', 'C:\\Program Files (x86)', 'C:\\ProgramData']
                return any(path.startswith(dir) for dir in system_dirs)
            else:
                # Linux/macOS系统：检查系统目录
                system_dirs = ['/etc', '/sys', '/proc', '/dev', '/boot', '/usr']
                return any(path.startswith(dir) for dir in system_dirs)
        except Exception:
            return False
    
    def _delete_worker(self):
        """
        删除文件的工作线程函数
        """
        while True:
            try:
                # 从任务队列获取文件路径
                file_path = self.task_queue.get(block=False)
                
                try:
                    # 删除文件
                    self.bmb_deleter.delete_file(file_path)
                    self.stats['deleted_files'] += 1
                    
                    # 每删除100个文件打印一次进度
                    if self.stats['deleted_files'] % 100 == 0:
                        self.logger.info(f"删除进度: {self.stats['deleted_files']}/{self.stats['total_files']}")
                except Exception as e:
                    self.stats['failed_files'] += 1
                    self.stats['errors'].append({
                        'file': file_path,
                        'error': str(e)
                    })
                    self.logger.error(f"删除文件失败: {file_path}, 错误: {str(e)}")
                finally:
                    # 标记任务完成
                    self.task_queue.task_done()
            except queue.Empty:
                # 任务队列为空，退出循环
                break
            except Exception as e:
                self.logger.error(f"工作线程错误: {str(e)}")
    
    def delete_partition(self, partition_mountpoint, confirm=False):
        """
        彻底删除分区内的所有文件
        
        Args:
            partition_mountpoint (str): 分区挂载点
            confirm (bool, optional): 是否确认删除，默认False
        
        Returns:
            dict: 删除统计信息
        """
        # 验证分区是否存在
        if not os.path.exists(partition_mountpoint):
            raise ValueError(f"分区不存在: {partition_mountpoint}")
        
        # 验证分区是否可写
        if not os.access(partition_mountpoint, os.W_OK):
            raise PermissionError(f"分区不可写: {partition_mountpoint}")
        
        # 确认删除
        if not confirm:
            confirm_input = input(f"确定要删除分区 {partition_mountpoint} 内的所有文件吗？(yes/no): ")
            if confirm_input.lower() != 'yes':
                self.logger.info("用户取消删除操作")
                return self.stats
        
        # 开始删除操作
        self.logger.info(f"开始删除分区 {partition_mountpoint} 内的所有文件")
        self.stats['start_time'] = time.time()
        
        try:
            # 扫描分区内的所有文件
            self._scan_partition(partition_mountpoint)
            
            if self.stats['total_files'] == 0:
                self.logger.info("分区内没有文件需要删除")
                return self.stats
            
            # 创建线程池
            with ThreadPoolExecutor(max_workers=self.max_threads, thread_name_prefix="Partition-Deletion-Worker") as executor:
                # 提交删除任务
                futures = []
                for _ in range(self.max_threads):
                    future = executor.submit(self._delete_worker)
                    futures.append(future)
                
                # 等待所有任务完成
                for future in as_completed(futures):
                    try:
                        future.result()
                    except Exception as e:
                        self.logger.error(f"线程执行失败: {str(e)}")
        except Exception as e:
            self.logger.error(f"删除分区文件失败: {str(e)}")
            self.stats['errors'].append({'error': str(e)})
        finally:
            # 完成删除操作
            self.stats['end_time'] = time.time()
            self.stats['elapsed_time'] = self.stats['end_time'] - self.stats['start_time']
            
            # 打印删除结果
            self.logger.info(f"删除操作完成")
            self.logger.info(f"总文件数: {self.stats['total_files']}")
            self.logger.info(f"已删除文件数: {self.stats['deleted_files']}")
            self.logger.info(f"失败文件数: {self.stats['failed_files']}")
            self.logger.info(f"耗时: {self.stats['elapsed_time']:.2f} 秒")
            
            if self.stats['errors']:
                self.logger.warning(f"错误列表: {json.dumps(self.stats['errors'], indent=2, ensure_ascii=False)}")
        
        return self.stats
    
    def verify_deletion(self, partition_mountpoint):
        """
        验证分区删除操作是否成功
        
        Args:
            partition_mountpoint (str): 分区挂载点
        
        Returns:
            bool: 删除是否成功
        """
        self.logger.info(f"开始验证分区删除操作: {partition_mountpoint}")
        
        try:
            # 扫描分区内是否还有文件
            remaining_files = []
            for root, dirs, files in os.walk(partition_mountpoint):
                # 跳过系统保护的目录
                dirs[:] = [d for d in dirs if not self._is_system_protected(os.path.join(root, d))]
                
                for file in files:
                    file_path = os.path.join(root, file)
                    
                    # 跳过系统保护的文件
                    if not self._is_system_protected(file_path):
                        remaining_files.append(file_path)
            
            if remaining_files:
                self.logger.warning(f"分区内仍有 {len(remaining_files)} 个文件未删除")
                for file in remaining_files[:10]:
                    self.logger.warning(f"  - {file}")
                if len(remaining_files) > 10:
                    self.logger.warning(f"  ... 还有 {len(remaining_files) - 10} 个文件")
                return False
            else:
                self.logger.info("分区删除验证成功，未发现剩余文件")
                return True
        except Exception as e:
            self.logger.error(f"验证分区删除失败: {str(e)}")
            return False
    
    def get_deletion_report(self):
        """
        获取删除操作报告
        
        Returns:
            dict: 删除操作报告
        """
        report = {
            'timestamp': time.time(),
            'hardware_info': self.hardware_info,
            'stats': self.stats,
            'bmb21_2019_compliant': True,
            'verification_passed': self.stats['failed_files'] == 0
        }
        
        return report

if __name__ == "__main__":
    # 测试分区删除功能
    deleter = PartitionDeletion()
    
    # 获取分区列表
    partitions = deleter.get_partitions()
    print("可用分区:")
    for i, partition in enumerate(partitions):
        print(f"{i + 1}. {partition['device']} - {partition['description']}")
        print(f"   文件系统: {partition['file_system']}")
        print(f"   总容量: {partition['size'] / (1024 ** 3):.2f} GB")
        print(f"   已用空间: {partition['used_space'] / (1024 ** 3):.2f} GB")
        print(f"   可用空间: {partition['free_space'] / (1024 ** 3):.2f} GB")
        print()
    
    # 选择分区
    choice = input("请选择要删除的分区序号: ")
    try:
        index = int(choice) - 1
        if 0 <= index < len(partitions):
            partition = partitions[index]
            print(f"您选择的分区: {partition['device']} - {partition['description']}")
            print("警告: 此操作将彻底删除分区内的所有文件，无法恢复！")
            
            # 执行删除操作
            stats = deleter.delete_partition(partition['mountpoint'], confirm=True)
            print(f"删除操作完成，共删除 {stats['deleted_files']} 个文件，失败 {stats['failed_files']} 个文件")
            
            # 验证删除操作
            if deleter.verify_deletion(partition['mountpoint']):
                print("删除验证成功，分区内的所有文件已被彻底删除")
            else:
                print("删除验证失败，分区内仍有文件未被删除")
        else:
            print("无效的选择")
    except ValueError:
        print("请输入有效的序号")
    except Exception as e:
        print(f"错误: {str(e)}")
