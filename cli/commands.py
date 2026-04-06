#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CLI 命令实现模块
实现加密、解密、删除等具体命令
"""

import os
import sys
import secrets
import string
import time
import argparse
from typing import Optional, List
from pathlib import Path

# 添加项目根目录到路径
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)


class BaseCommand:
    """
    命令基类
    """
    
    def __init__(self, ui, file_selector):
        """
        初始化命令
        
        Args:
            ui: UIHelper实例
            file_selector: FileSelector实例
        """
        self.ui = ui
        self.file_selector = file_selector
    
    def execute(self, args: argparse.Namespace) -> int:
        """
        执行命令
        
        Args:
            args: 命令行参数
            
        Returns:
            int: 退出码
        """
        raise NotImplementedError("子类必须实现execute方法")


class EncryptCommand(BaseCommand):
    """
    加密命令
    """
    
    def execute(self, args: argparse.Namespace) -> int:
        """
        执行加密命令
        
        Args:
            args: 命令行参数
            
        Returns:
            int: 退出码
        """
        self.ui.print_header("加密模式")
        
        # 获取输入路径
        input_path = self._get_input_path(args)
        if not input_path:
            self.ui.print_error("未指定输入路径")
            return 1
        
        # 获取输出路径
        output_path = self._get_output_path(args, input_path)
        if not output_path:
            self.ui.print_error("未指定输出路径")
            return 1
        
        # 生成或获取密钥
        master_key = self._generate_key()
        
        # 获取选项
        delete_original = args.delete_original if hasattr(args, 'delete_original') else False
        compression_level = args.compression if hasattr(args, 'compression') else 9
        
        # 确认操作
        self.ui.print_info("操作确认")
        print(f"  输入路径: {input_path}")
        print(f"  输出路径: {output_path}")
        print(f"  压缩级别: {compression_level}")
        print(f"  删除原文件: {'是' if delete_original else '否'}")
        
        if not self.ui.get_confirmation("确认开始加密?", default=True):
            self.ui.print_warning("操作已取消")
            return 0
        
        # 执行加密
        return self._perform_encryption(input_path, output_path, master_key, delete_original, compression_level)
    
    def _get_input_path(self, args: argparse.Namespace) -> Optional[str]:
        """
        获取输入路径
        
        Args:
            args: 命令行参数
            
        Returns:
            Optional[str]: 输入路径
        """
        # 优先使用命令行参数
        if hasattr(args, 'input') and args.input:
            return os.path.abspath(os.path.expanduser(args.input))
        if hasattr(args, 'directory') and args.directory:
            return os.path.abspath(os.path.expanduser(args.directory))
        
        # 交互式选择
        self.ui.print_info("请选择要加密的文件或文件夹")
        options = ["选择文件", "选择文件夹"]
        choice = self.ui.get_choice("请选择类型:", options)
        
        if choice == 0:  # 选择文件
            return self.file_selector.select_input_file(self.ui)
        else:  # 选择文件夹
            return self.file_selector.select_folder(self.ui)
    
    def _get_output_path(self, args: argparse.Namespace, input_path: str) -> Optional[str]:
        """
        获取输出路径
        
        Args:
            args: 命令行参数
            input_path: 输入路径
            
        Returns:
            Optional[str]: 输出路径
        """
        # 优先使用命令行参数
        if hasattr(args, 'output') and args.output:
            output_path = os.path.abspath(os.path.expanduser(args.output))
            if not output_path.endswith('.7z.enc'):
                output_path += '.7z.enc'
            return output_path
        
        # 交互式选择
        default_name = os.path.basename(input_path) + '.7z.enc'
        output_path = self.file_selector.select_output_path(self.ui, default_name=default_name)
        
        if output_path and not output_path.endswith('.7z.enc'):
            output_path += '.7z.enc'
        
        return output_path
    
    def _generate_key(self) -> bytes:
        """
        生成随机密钥
        
        Returns:
            bytes: 密钥
        """
        # 生成32位随机密钥
        alphabet = string.ascii_letters + string.digits + string.punctuation
        key = ''.join(secrets.choice(alphabet) for _ in range(32))
        return key.encode('utf-8')
    
    def _perform_encryption(self, input_path: str, output_path: str, master_key: bytes, 
                           delete_original: bool, compression_level: int) -> int:
        """
        执行加密操作
        
        Args:
            input_path: 输入路径
            output_path: 输出路径
            master_key: 主密钥
            delete_original: 是否删除原文件
            compression_level: 压缩级别
            
        Returns:
            int: 退出码
        """
        try:
            # 导入加密模块
            from encryption.pre_check import EncryptionPreCheck
            from encryption.compression import Compression
            from encryption.hybrid_encryption import HybridEncryption
            from encryption.cleanup import EncryptionCleanup
            
            # 1. 加密前预检
            self.ui.print_info("开始加密前预检...")
            pre_check = EncryptionPreCheck()
            if not pre_check.run_all_checks(input_path):
                self.ui.print_error(f"预检失败: {'; '.join(pre_check.errors)}")
                return 1
            self.ui.print_success("预检通过")
            
            # 2. 7Z压缩
            self.ui.print_info("开始7Z压缩...")
            compression = Compression()
            
            # 进度回调
            def progress_callback(progress):
                self.ui.show_progress(progress, 100, prefix="压缩进度")
            
            compressed_file, sha512_hash, sm3_hash = compression.compress(
                input_path,
                progress_callback=progress_callback
            )
            self.ui.print_success(f"压缩完成: {compressed_file}")
            
            # 3. 混合加密
            self.ui.print_info("开始混合加密...")
            hybrid_encryption = HybridEncryption()
            
            # 模拟进度
            for i in range(0, 101, 10):
                self.ui.show_progress(i, 100, prefix="加密进度")
                time.sleep(0.05)
            
            encrypted_file, _, _ = hybrid_encryption.encrypt(
                compressed_file, master_key, output_path, sha512_hash, sm3_hash
            )
            self.ui.print_success(f"加密完成: {encrypted_file}")
            
            # 4. 清理操作
            self.ui.print_info("开始清理操作...")
            cleanup = EncryptionCleanup()
            cleanup.delete_temp_file(compressed_file)
            
            if delete_original:
                if os.path.isfile(input_path):
                    cleanup.delete_temp_file(input_path)
                else:
                    cleanup.delete_original_folder(input_path)
                self.ui.print_success("已删除原始文件/文件夹")
            
            cleanup.clear_memory()
            
            # 显示结果
            self.ui.print_divider('=')
            self.ui.print_success("加密成功完成！")
            print(f"  加密包路径: {encrypted_file}")
            print(f"  SHA-512: {sha512_hash}")
            print(f"  SM3: {sm3_hash}")
            self.ui.print_divider('=')
            self.ui.print_warning("请妥善保存以下主密钥，解密时需要使用")
            print(f"  主密钥: {master_key.decode('utf-8')}")
            self.ui.print_divider('=')
            
            return 0
            
        except Exception as e:
            self.ui.print_error(f"加密失败: {str(e)}")
            return 1


class DecryptCommand(BaseCommand):
    """
    解密命令
    """
    
    def execute(self, args: argparse.Namespace) -> int:
        """
        执行解密命令
        
        Args:
            args: 命令行参数
            
        Returns:
            int: 退出码
        """
        self.ui.print_header("解密模式")
        
        # 获取加密包路径
        encrypted_file = self._get_encrypted_file(args)
        if not encrypted_file:
            self.ui.print_error("未指定加密包路径")
            return 1
        
        # 获取输出文件夹
        output_folder = self._get_output_folder(args, encrypted_file)
        if not output_folder:
            self.ui.print_error("未指定输出文件夹")
            return 1
        
        # 获取密钥
        master_key = self._get_key(args)
        if not master_key:
            self.ui.print_error("未提供主密钥")
            return 1
        
        # 获取选项
        delete_encrypted = args.delete_encrypted if hasattr(args, 'delete_encrypted') else False
        
        # 确认操作
        self.ui.print_info("操作确认")
        print(f"  加密包: {encrypted_file}")
        print(f"  输出文件夹: {output_folder}")
        print(f"  删除加密包: {'是' if delete_encrypted else '否'}")
        
        if not self.ui.get_confirmation("确认开始解密?", default=True):
            self.ui.print_warning("操作已取消")
            return 0
        
        # 执行解密
        return self._perform_decryption(encrypted_file, output_folder, master_key, delete_encrypted)
    
    def _get_encrypted_file(self, args: argparse.Namespace) -> Optional[str]:
        """
        获取加密包路径
        
        Args:
            args: 命令行参数
            
        Returns:
            Optional[str]: 加密包路径
        """
        # 优先使用命令行参数
        if hasattr(args, 'input') and args.input:
            return os.path.abspath(os.path.expanduser(args.input))
        
        # 交互式选择
        return self.file_selector.select_encrypted_file(self.ui)
    
    def _get_output_folder(self, args: argparse.Namespace, encrypted_file: str) -> Optional[str]:
        """
        获取输出文件夹
        
        Args:
            args: 命令行参数
            encrypted_file: 加密包路径
            
        Returns:
            Optional[str]: 输出文件夹路径
        """
        # 优先使用命令行参数
        if hasattr(args, 'output') and args.output:
            return os.path.abspath(os.path.expanduser(args.output))
        
        # 交互式选择
        default_name = os.path.basename(encrypted_file).replace('.7z.enc', '_decrypted')
        return self.file_selector.select_output_path(self.ui, default_name=default_name, is_folder=True)
    
    def _get_key(self, args: argparse.Namespace) -> Optional[bytes]:
        """
        获取主密钥
        
        Args:
            args: 命令行参数
            
        Returns:
            Optional[bytes]: 主密钥
        """
        # 优先使用命令行参数（不推荐）
        if hasattr(args, 'key') and args.key:
            self.ui.print_warning("通过命令行参数传递密钥存在安全风险，建议交互式输入")
            return args.key.encode('utf-8')
        
        # 交互式输入
        key = self.ui.get_input("请输入主密钥", required=True)
        return key.encode('utf-8') if key else None
    
    def _perform_decryption(self, encrypted_file: str, output_folder: str, 
                           master_key: bytes, delete_encrypted: bool) -> int:
        """
        执行解密操作
        
        Args:
            encrypted_file: 加密包路径
            output_folder: 输出文件夹
            master_key: 主密钥
            delete_encrypted: 是否删除加密包
            
        Returns:
            int: 退出码
        """
        try:
            # 导入解密模块
            from decryption.pre_check import DecryptionPreCheck
            from decryption.hybrid_decryption import HybridDecryption
            from decryption.decompression import Decompression
            from decryption.cleanup import DecryptionCleanup
            
            # 1. 解密前预检
            self.ui.print_info("开始解密前预检...")
            pre_check = DecryptionPreCheck()
            if not pre_check.run_all_checks(encrypted_file, master_key):
                self.ui.print_error("预检失败")
                return 1
            self.ui.print_success("预检通过")
            
            # 2. 混合解密
            self.ui.print_info("开始混合解密...")
            hybrid_decryption = HybridDecryption()
            
            # 模拟进度
            for i in range(0, 51, 10):
                self.ui.show_progress(i, 100, prefix="解密进度")
                time.sleep(0.05)
            
            decrypted_file, sha512_hash, sm3_hash = hybrid_decryption.decrypt(
                encrypted_file, master_key
            )
            self.ui.print_success(f"解密完成: {decrypted_file}")
            
            # 3. 7Z解压
            self.ui.print_info("开始7Z解压...")
            decompression = Decompression()
            
            # 进度回调
            def progress_callback(progress):
                self.ui.show_progress(progress + 50, 100, prefix="解压进度")
            
            decompression.decompress(decrypted_file, output_folder, progress_callback=progress_callback)
            self.ui.print_success(f"解压完成: {output_folder}")
            
            # 4. 清理操作
            self.ui.print_info("开始清理操作...")
            cleanup = DecryptionCleanup()
            cleanup.delete_temp_file(decrypted_file)
            
            if delete_encrypted:
                cleanup.delete_encrypted_file(encrypted_file)
                self.ui.print_success("已删除加密包")
            
            cleanup.clear_memory()
            
            # 显示结果
            self.ui.print_divider('=')
            self.ui.print_success("解密成功完成！")
            print(f"  输出文件夹: {output_folder}")
            print(f"  SHA-512: {sha512_hash}")
            print(f"  SM3: {sm3_hash}")
            self.ui.print_divider('=')
            
            return 0
            
        except Exception as e:
            self.ui.print_error(f"解密失败: {str(e)}")
            return 1


class DeleteCommand(BaseCommand):
    """
    删除命令
    """
    
    def execute(self, args: argparse.Namespace) -> int:
        """
        执行删除命令
        
        Args:
            args: 命令行参数
            
        Returns:
            int: 退出码
        """
        self.ui.print_header("文件删除模式")
        
        # 显示警告
        self.ui.print_warning("此操作将永久删除文件，无法恢复！")
        
        # 获取目标路径
        target_path, delete_type = self._get_target_path(args)
        if not target_path:
            self.ui.print_error("未指定目标路径")
            return 1
        
        # 确认操作
        self.ui.print_info("操作确认")
        print(f"  目标路径: {target_path}")
        print(f"  删除类型: {'文件' if delete_type == 'file' else '文件夹'}")
        print(f"  删除标准: BMB21-2019")
        
        if not self.ui.get_confirmation("确认彻底删除?", default=False):
            self.ui.print_warning("操作已取消")
            return 0
        
        # 二次确认
        self.ui.print_warning("这是最后一次确认，删除后数据将无法恢复！")
        if not self.ui.get_confirmation("确定要彻底删除吗?", default=False):
            self.ui.print_warning("操作已取消")
            return 0
        
        # 执行删除
        return self._perform_deletion(target_path, delete_type)
    
    def _get_target_path(self, args: argparse.Namespace) -> tuple:
        """
        获取目标路径和类型
        
        Args:
            args: 命令行参数
            
        Returns:
            tuple: (路径, 类型)
        """
        # 优先使用命令行参数
        if hasattr(args, 'file') and args.file:
            return os.path.abspath(os.path.expanduser(args.file)), 'file'
        if hasattr(args, 'directory') and args.directory:
            return os.path.abspath(os.path.expanduser(args.directory)), 'folder'
        
        # 交互式选择
        options = ["删除文件", "删除文件夹"]
        choice = self.ui.get_choice("请选择删除类型:", options)
        
        if choice == 0:  # 删除文件
            path = self.file_selector.select_input_file(self.ui)
            return path, 'file'
        else:  # 删除文件夹
            path = self.file_selector.select_folder(self.ui)
            return path, 'folder'
    
    def _perform_deletion(self, target_path: str, delete_type: str) -> int:
        """
        执行删除操作
        
        Args:
            target_path: 目标路径
            delete_type: 删除类型
            
        Returns:
            int: 退出码
        """
        try:
            # 导入删除模块
            from deletion.bmb21_2019 import BMB212019Deletion
            from deletion.verification import DeletionVerification
            
            # 创建删除工具
            self.ui.print_info("开始使用 BMB21-2019 标准删除...")
            deletion_tool = BMB212019Deletion()
            
            # 模拟进度
            for i in range(0, 81, 5):
                self.ui.show_progress(i, 100, prefix="删除进度")
                time.sleep(0.05)
            
            # 执行删除
            if delete_type == 'file':
                deletion_tool.delete_file(target_path)
            else:
                deletion_tool.delete_folder(target_path)
            
            self.ui.show_progress(80, 100, prefix="删除进度")
            
            # 验证删除结果
            self.ui.print_info("开始验证删除结果...")
            verification = DeletionVerification()
            
            if delete_type == 'file':
                success, result = verification.verify_file_deletion(target_path)
            else:
                success, result = verification.verify_folder_deletion(target_path)
            
            self.ui.show_progress(100, 100, prefix="删除进度")
            
            # 显示结果
            self.ui.print_divider('=')
            if success:
                self.ui.print_success("删除成功完成！")
            else:
                self.ui.print_warning("删除完成，但验证未完全通过")
            print(f"  验证结果: {result}")
            self.ui.print_divider('=')
            
            return 0
            
        except Exception as e:
            self.ui.print_error(f"删除失败: {str(e)}")
            return 1
