#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FullCycleFileShield CLI 主模块
提供命令行界面，支持加密、解密、删除等操作
"""

import os
import sys
import argparse
import getpass
import secrets
import string
from typing import Optional, List, Tuple
from pathlib import Path

# 添加项目根目录到路径
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from cli.ui import UIHelper
from cli.file_selector import FileSelector
from cli.commands import EncryptCommand, DecryptCommand, DeleteCommand


class CLI:
    """
    命令行界面主类
    """
    
    def __init__(self):
        """
        初始化CLI
        """
        self.ui = UIHelper()
        self.file_selector = FileSelector()
        self.parser = self._create_parser()
    
    def _create_parser(self) -> argparse.ArgumentParser:
        """
        创建命令行参数解析器
        
        Returns:
            argparse.ArgumentParser: 参数解析器
        """
        parser = argparse.ArgumentParser(
            prog='fcfs',
            description='FullCycleFileShield - 文件加密解密工具（命令行模式）',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog='''
使用示例:
  %(prog)s encrypt                    交互式加密
  %(prog)s encrypt -i /path/to/file   指定输入文件进行加密
  %(prog)s decrypt                    交互式解密
  %(prog)s delete                     交互式删除
  %(prog)s gui                        启动图形界面

更多信息:
  请访问项目文档或运行 %(prog)s <command> --help 查看详细帮助
'''
        )
        
        subparsers = parser.add_subparsers(dest='command', help='可用命令')
        
        # 加密命令
        encrypt_parser = subparsers.add_parser(
            'encrypt',
            help='加密文件或文件夹',
            description='将文件或文件夹加密为加密包',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog='''
加密示例:
  %(prog)s encrypt                    交互式选择文件并加密
  %(prog)s encrypt -i file.txt        加密指定文件
  %(prog)s encrypt -d /path/to/folder 加密指定文件夹
  %(prog)s encrypt -o output.7z.enc   指定输出路径
  %(prog)s encrypt --delete-original  加密后删除原文件
'''
        )
        encrypt_parser.add_argument('-i', '--input', help='输入文件路径')
        encrypt_parser.add_argument('-d', '--directory', help='输入文件夹路径')
        encrypt_parser.add_argument('-o', '--output', help='输出加密包路径')
        encrypt_parser.add_argument('-k', '--key', help='主密钥（不推荐在命令行中直接指定）')
        encrypt_parser.add_argument('--delete-original', action='store_true', help='加密完成后删除原始文件')
        encrypt_parser.add_argument('--compression', type=int, choices=range(1, 10), default=9, help='压缩级别（1-9，默认9）')
        
        # 解密命令
        decrypt_parser = subparsers.add_parser(
            'decrypt',
            help='解密加密包',
            description='将加密包解密为原始文件或文件夹',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog='''
解密示例:
  %(prog)s decrypt                    交互式选择加密包并解密
  %(prog)s decrypt -i package.7z.enc  解密指定加密包
  %(prog)s decrypt -o /output/folder  指定输出文件夹
  %(prog)s decrypt --delete-encrypted 解密后删除加密包
'''
        )
        decrypt_parser.add_argument('-i', '--input', help='输入加密包路径')
        decrypt_parser.add_argument('-o', '--output', help='输出文件夹路径')
        decrypt_parser.add_argument('-k', '--key', help='主密钥（不推荐在命令行中直接指定）')
        decrypt_parser.add_argument('--delete-encrypted', action='store_true', help='解密完成后删除加密包')
        
        # 删除命令
        delete_parser = subparsers.add_parser(
            'delete',
            help='彻底删除文件或文件夹',
            description='按照 BMB21-2019 标准彻底删除文件或文件夹',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog='''
删除示例:
  %(prog)s delete                     交互式选择文件并删除
  %(prog)s delete -f file.txt         删除指定文件
  %(prog)s delete -d /path/to/folder  删除指定文件夹
'''
        )
        delete_parser.add_argument('-f', '--file', help='要删除的文件路径')
        delete_parser.add_argument('-d', '--directory', help='要删除的文件夹路径')
        
        # GUI命令
        gui_parser = subparsers.add_parser(
            'gui',
            help='启动图形界面',
            description='启动 FullCycleFileShield 图形界面'
        )
        
        # 版本信息
        parser.add_argument('-v', '--version', action='version', version='%(prog)s 1.0.0')
        
        return parser
    
    def run(self, args: Optional[List[str]] = None) -> int:
        """
        运行CLI
        
        Args:
            args: 命令行参数列表
            
        Returns:
            int: 退出码（0表示成功，非0表示失败）
        """
        parsed_args = self.parser.parse_args(args)
        
        # 显示欢迎信息
        if parsed_args.command:
            self.ui.show_welcome()
        
        try:
            if parsed_args.command == 'encrypt':
                return self._handle_encrypt(parsed_args)
            elif parsed_args.command == 'decrypt':
                return self._handle_decrypt(parsed_args)
            elif parsed_args.command == 'delete':
                return self._handle_delete(parsed_args)
            elif parsed_args.command == 'gui':
                return self._handle_gui()
            else:
                # 没有指定命令，显示帮助
                self.parser.print_help()
                return 0
        except KeyboardInterrupt:
            self.ui.print_warning("\n操作已取消")
            return 130
        except Exception as e:
            self.ui.print_error(f"发生错误: {str(e)}")
            return 1
    
    def _handle_encrypt(self, args: argparse.Namespace) -> int:
        """
        处理加密命令
        
        Args:
            args: 解析后的参数
            
        Returns:
            int: 退出码
        """
        command = EncryptCommand(self.ui, self.file_selector)
        return command.execute(args)
    
    def _handle_decrypt(self, args: argparse.Namespace) -> int:
        """
        处理解密命令
        
        Args:
            args: 解析后的参数
            
        Returns:
            int: 退出码
        """
        command = DecryptCommand(self.ui, self.file_selector)
        return command.execute(args)
    
    def _handle_delete(self, args: argparse.Namespace) -> int:
        """
        处理删除命令
        
        Args:
            args: 解析后的参数
            
        Returns:
            int: 退出码
        """
        command = DeleteCommand(self.ui, self.file_selector)
        return command.execute(args)
    
    def _handle_gui(self) -> int:
        """
        处理GUI命令
        
        Returns:
            int: 退出码
        """
        self.ui.print_info("正在启动图形界面...")
        try:
            from gui.main_window import MainWindow
            from PyQt5.QtWidgets import QApplication
            
            app = QApplication(sys.argv)
            window = MainWindow()
            return app.exec_()
        except ImportError as e:
            self.ui.print_error(f"无法启动图形界面: {str(e)}")
            self.ui.print_info("请确保已安装 PyQt5: python -m pip install PyQt5")
            return 1


def main():
    """
    CLI入口函数
    """
    cli = CLI()
    sys.exit(cli.run())


if __name__ == '__main__':
    main()
