#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CLI UI 辅助模块
提供用户友好的交互提示、颜色输出和格式化显示
"""

import os
import sys
import shutil
from typing import Optional, List


class Colors:
    """
    ANSI颜色代码
    """
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    
    # 前景色
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # 背景色
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'


class UIHelper:
    """
    UI辅助类，提供用户友好的交互功能
    """
    
    def __init__(self):
        """
        初始化UIHelper
        """
        self.colors = Colors()
        self.use_colors = self._supports_color()
        self.terminal_width = self._get_terminal_width()
    
    def _supports_color(self) -> bool:
        """
        检查终端是否支持颜色输出
        
        Returns:
            bool: 是否支持颜色
        """
        # Windows系统检查
        if sys.platform == 'win32':
            # Windows 10 版本 1511 及以上支持ANSI颜色
            try:
                import ctypes
                kernel32 = ctypes.windll.kernel32
                # 启用虚拟终端处理
                kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
                return True
            except:
                return False
        
        # Unix/Linux/Mac系统检查
        return hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()
    
    def _get_terminal_width(self) -> int:
        """
        获取终端宽度
        
        Returns:
            int: 终端宽度
        """
        try:
            return shutil.get_terminal_size().columns
        except:
            return 80
    
    def _colorize(self, text: str, color: str) -> str:
        """
        为文本添加颜色
        
        Args:
            text: 原始文本
            color: 颜色代码
            
        Returns:
            str: 带颜色的文本
        """
        if self.use_colors:
            return f"{color}{text}{self.colors.RESET}"
        return text
    
    def print_colored(self, text: str, color: str, bold: bool = False):
        """
        打印带颜色的文本
        
        Args:
            text: 文本内容
            color: 颜色代码
            bold: 是否加粗
        """
        if bold:
            text = self._colorize(text, self.colors.BOLD + color)
        else:
            text = self._colorize(text, color)
        print(text)
    
    def print_success(self, message: str):
        """
        打印成功消息
        
        Args:
            message: 消息内容
        """
        self.print_colored(f"✓ {message}", self.colors.GREEN)
    
    def print_error(self, message: str):
        """
        打印错误消息
        
        Args:
            message: 消息内容
        """
        self.print_colored(f"✗ {message}", self.colors.RED)
    
    def print_warning(self, message: str):
        """
        打印警告消息
        
        Args:
            message: 消息内容
        """
        self.print_colored(f"⚠ {message}", self.colors.YELLOW)
    
    def print_info(self, message: str):
        """
        打印信息消息
        
        Args:
            message: 消息内容
        """
        self.print_colored(f"ℹ {message}", self.colors.CYAN)
    
    def print_header(self, message: str):
        """
        打印标题
        
        Args:
            message: 消息内容
        """
        self.print_colored(message, self.colors.BLUE, bold=True)
    
    def print_divider(self, char: str = '=', length: Optional[int] = None):
        """
        打印分隔线
        
        Args:
            char: 分隔字符
            length: 分隔线长度
        """
        if length is None:
            length = self.terminal_width
        print(char * length)
    
    def show_welcome(self):
        """
        显示欢迎信息
        """
        print()
        self.print_divider('=')
        self.print_colored("  FullCycleFileShield (FCFS) - 命令行模式", self.colors.CYAN, bold=True)
        self.print_colored("  文件加密解密工具 - 符合 GB/T39786-2021 第 5 级标准", self.colors.DIM)
        self.print_divider('=')
        print()
    
    def show_disclaimer(self) -> bool:
        """
        显示免责声明并获取用户确认
        
        Returns:
            bool: 用户是否同意
        """
        self.print_warning("免责声明")
        self.print_divider('-')
        print("""
1. 使用风险
   - 本软件仅供学习和研究使用，请勿用于非法用途
   - 请确保您对所加密/删除的文件拥有合法所有权
   - 使用本软件可能导致数据丢失，请提前备份重要数据

2. 责任限制
   - 开发团队不对使用本软件造成的任何直接或间接损失负责
   - 开发团队不对软件的安全性和可靠性做出任何保证
   - 开发团队不承担任何因使用本软件导致的法律责任

3. 不保证条款
   - 本软件按"原样"提供，不提供任何形式的保证
   - 不保证软件无错误、无漏洞或适合特定用途
   - 不保证软件与所有硬件和软件兼容
""")
        self.print_divider('-')
        
        while True:
            response = input(self._colorize("您是否同意以上条款并继续使用？(yes/no): ", self.colors.YELLOW)).strip().lower()
            if response in ('yes', 'y', '是'):
                return True
            elif response in ('no', 'n', '否'):
                return False
            else:
                self.print_error("请输入 'yes' 或 'no'")
    
    def get_input(self, prompt: str, required: bool = True, default: Optional[str] = None) -> str:
        """
        获取用户输入
        
        Args:
            prompt: 提示文本
            required: 是否必填
            default: 默认值
            
        Returns:
            str: 用户输入
        """
        while True:
            if default:
                full_prompt = f"{prompt} [{default}]: "
            else:
                full_prompt = f"{prompt}: "
            
            value = input(self._colorize(full_prompt, self.colors.CYAN)).strip()
            
            if not value:
                if default:
                    return default
                elif not required:
                    return ""
                else:
                    self.print_error("此项为必填项，请输入有效值")
                    continue
            
            return value
    
    def get_password(self, prompt: str = "请输入密码", confirm: bool = True) -> str:
        """
        获取密码输入（隐藏显示）
        
        Args:
            prompt: 提示文本
            confirm: 是否需要确认密码
            
        Returns:
            str: 密码
        """
        import getpass
        
        while True:
            password = getpass.getpass(self._colorize(f"{prompt}: ", self.colors.CYAN))
            
            if not password:
                self.print_error("密码不能为空")
                continue
            
            if confirm:
                confirm_password = getpass.getpass(self._colorize("请再次输入密码以确认: ", self.colors.CYAN))
                if password != confirm_password:
                    self.print_error("两次输入的密码不一致，请重新输入")
                    continue
            
            return password
    
    def get_choice(self, prompt: str, options: List[str], default: Optional[int] = None) -> int:
        """
        获取用户选择
        
        Args:
            prompt: 提示文本
            options: 选项列表
            default: 默认选项索引
            
        Returns:
            int: 选择的索引
        """
        self.print_info(prompt)
        for i, option in enumerate(options, 1):
            if default is not None and i - 1 == default:
                print(f"  {self._colorize(f'[{i}]', self.colors.GREEN)} {option}")
            else:
                print(f"  [{i}] {option}")
        
        while True:
            if default is not None:
                full_prompt = f"请选择 [1-{len(options)}] (默认: {default + 1}): "
            else:
                full_prompt = f"请选择 [1-{len(options)}]: "
            
            choice = input(self._colorize(full_prompt, self.colors.CYAN)).strip()
            
            if not choice and default is not None:
                return default
            
            try:
                index = int(choice) - 1
                if 0 <= index < len(options):
                    return index
                else:
                    self.print_error(f"请输入 1 到 {len(options)} 之间的数字")
            except ValueError:
                self.print_error("请输入有效的数字")
    
    def get_confirmation(self, prompt: str, default: bool = False) -> bool:
        """
        获取用户确认
        
        Args:
            prompt: 提示文本
            default: 默认值
            
        Returns:
            bool: 用户是否确认
        """
        default_str = "Y/n" if default else "y/N"
        full_prompt = f"{prompt} [{default_str}]: "
        
        while True:
            response = input(self._colorize(full_prompt, self.colors.YELLOW)).strip().lower()
            
            if not response:
                return default
            elif response in ('yes', 'y', '是'):
                return True
            elif response in ('no', 'n', '否'):
                return False
            else:
                self.print_error("请输入 'yes' 或 'no'")
    
    def show_progress(self, current: int, total: int, prefix: str = "进度", suffix: str = ""):
        """
        显示进度条
        
        Args:
            current: 当前进度
            total: 总进度
            prefix: 前缀文本
            suffix: 后缀文本
        """
        if total == 0:
            return
        
        percent = min(100, int(100 * current / total))
        bar_length = min(50, self.terminal_width - len(prefix) - len(suffix) - 20)
        filled_length = int(bar_length * current / total)
        
        bar = '█' * filled_length + '░' * (bar_length - filled_length)
        
        if self.use_colors:
            if percent < 30:
                color = self.colors.RED
            elif percent < 70:
                color = self.colors.YELLOW
            else:
                color = self.colors.GREEN
            
            print(f'\r{prefix}: {self._colorize(bar, color)} {percent}% {suffix}', end='')
        else:
            print(f'\r{prefix}: {bar} {percent}% {suffix}', end='')
        
        if current >= total:
            print()
    
    def show_file_info(self, file_path: str):
        """
        显示文件信息
        
        Args:
            file_path: 文件路径
        """
        if not os.path.exists(file_path):
            self.print_error(f"文件不存在: {file_path}")
            return
        
        size = os.path.getsize(file_path)
        size_str = self._format_size(size)
        
        self.print_info("文件信息")
        print(f"  路径: {file_path}")
        print(f"  大小: {size_str}")
        print(f"  修改时间: {self._format_time(os.path.getmtime(file_path))}")
    
    def _format_size(self, size: int) -> str:
        """
        格式化文件大小
        
        Args:
            size: 字节数
            
        Returns:
            str: 格式化后的大小
        """
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} PB"
    
    def _format_time(self, timestamp: float) -> str:
        """
        格式化时间戳
        
        Args:
            timestamp: 时间戳
            
        Returns:
            str: 格式化后的时间
        """
        from datetime import datetime
        return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
    
    def clear_screen(self):
        """
        清屏
        """
        if sys.platform == 'win32':
            os.system('cls')
        else:
            os.system('clear')
    
    def pause(self):
        """
        暂停等待用户按键
        """
        input(self._colorize("\n按回车键继续...", self.colors.DIM))
