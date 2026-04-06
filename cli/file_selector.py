#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件选择器模块
支持从默认文件夹选择或手动输入绝对路径
"""

import os
import glob
from typing import List, Optional, Tuple
from pathlib import Path


class FileSelector:
    """
    文件选择器类
    提供两种文件路径设置方式：
    1. 从预设的默认文件夹中选择文件
    2. 手动输入文件的绝对路径
    """
    
    # 默认文件夹配置
    DEFAULT_FOLDERS = {
        'documents': ('文档', [
            os.path.expanduser('~/Documents'),
            os.path.expanduser('~/文档'),
        ]),
        'downloads': ('下载', [
            os.path.expanduser('~/Downloads'),
            os.path.expanduser('~/下载'),
        ]),
        'desktop': ('桌面', [
            os.path.expanduser('~/Desktop'),
            os.path.expanduser('~/桌面'),
        ]),
        'home': ('用户目录', [
            os.path.expanduser('~'),
        ]),
    }
    
    def __init__(self):
        """
        初始化文件选择器
        """
        self.default_folder_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'default_files')
        self._ensure_default_folder_exists()
    
    def _ensure_default_folder_exists(self):
        """
        确保默认文件夹存在
        """
        if not os.path.exists(self.default_folder_path):
            try:
                os.makedirs(self.default_folder_path, exist_ok=True)
            except:
                pass
    
    def get_available_folders(self) -> List[Tuple[str, str]]:
        """
        获取可用的默认文件夹列表
        
        Returns:
            List[Tuple[str, str]]: 文件夹列表，每项为(显示名称, 路径)
        """
        folders = []
        
        # 添加系统默认文件夹
        for key, (name, paths) in self.DEFAULT_FOLDERS.items():
            for path in paths:
                if os.path.exists(path):
                    folders.append((name, path))
                    break
        
        # 添加应用程序默认文件夹
        if os.path.exists(self.default_folder_path):
            folders.append(('默认文件夹', self.default_folder_path))
        
        return folders
    
    def select_file_from_folder(self, ui, folder_path: str, pattern: str = '*') -> Optional[str]:
        """
        从指定文件夹中选择文件
        
        Args:
            ui: UIHelper实例
            folder_path: 文件夹路径
            pattern: 文件匹配模式
            
        Returns:
            Optional[str]: 选中的文件路径，取消则返回None
        """
        if not os.path.exists(folder_path):
            ui.print_error(f"文件夹不存在: {folder_path}")
            return None
        
        # 获取文件列表
        try:
            files = []
            for item in os.listdir(folder_path):
                item_path = os.path.join(folder_path, item)
                if os.path.isfile(item_path):
                    if pattern == '*' or item.endswith(pattern.replace('*', '')):
                        files.append(item)
            
            if not files:
                ui.print_warning(f"文件夹中没有匹配的文件: {folder_path}")
                return None
            
            # 排序文件列表
            files.sort()
            
            # 显示文件列表
            ui.print_info(f"文件夹: {folder_path}")
            ui.print_divider('-')
            
            options = files + ['[返回上级目录]', '[手动输入路径]']
            choice = ui.get_choice("请选择文件:", options, default=None)
            
            if choice == len(files):  # 返回上级目录
                parent = os.path.dirname(folder_path)
                if parent and parent != folder_path:
                    return self.select_file_from_folder(ui, parent, pattern)
                return None
            elif choice == len(files) + 1:  # 手动输入路径
                return self.manual_input_path(ui, must_exist=True)
            else:
                return os.path.join(folder_path, files[choice])
                
        except Exception as e:
            ui.print_error(f"读取文件夹失败: {str(e)}")
            return None
    
    def select_folder(self, ui, start_path: Optional[str] = None) -> Optional[str]:
        """
        选择文件夹
        
        Args:
            ui: UIHelper实例
            start_path: 起始路径
            
        Returns:
            Optional[str]: 选中的文件夹路径，取消则返回None
        """
        if start_path is None:
            start_path = os.path.expanduser('~')
        
        if not os.path.exists(start_path):
            start_path = os.path.expanduser('~')
        
        current_path = start_path
        
        while True:
            try:
                # 获取子文件夹列表
                items = []
                folders = []
                
                for item in os.listdir(current_path):
                    item_path = os.path.join(current_path, item)
                    if os.path.isdir(item_path):
                        folders.append(item)
                
                folders.sort()
                
                # 显示当前路径和选项
                ui.print_info(f"当前路径: {current_path}")
                ui.print_divider('-')
                
                options = ['[选择当前文件夹]'] + folders + ['[返回上级目录]', '[手动输入路径]']
                choice = ui.get_choice("请选择文件夹:", options, default=None)
                
                if choice == 0:  # 选择当前文件夹
                    return current_path
                elif choice == len(options) - 1:  # 手动输入路径
                    return self.manual_input_path(ui, must_exist=True, is_folder=True)
                elif choice == len(options) - 2:  # 返回上级目录
                    parent = os.path.dirname(current_path)
                    if parent and parent != current_path:
                        current_path = parent
                    continue
                else:  # 进入子文件夹
                    current_path = os.path.join(current_path, folders[choice - 1])
                    
            except PermissionError:
                ui.print_error("没有权限访问该文件夹")
                return None
            except Exception as e:
                ui.print_error(f"读取文件夹失败: {str(e)}")
                return None
    
    def manual_input_path(self, ui, must_exist: bool = True, is_folder: bool = False) -> Optional[str]:
        """
        手动输入文件/文件夹路径
        
        Args:
            ui: UIHelper实例
            must_exist: 是否必须存在
            is_folder: 是否必须是文件夹
            
        Returns:
            Optional[str]: 输入的路径，取消则返回None
        """
        item_type = "文件夹" if is_folder else "文件"
        prompt = f"请输入{item_type}的绝对路径"
        
        while True:
            path = ui.get_input(prompt, required=False)
            
            if not path:
                return None
            
            # 展开用户目录
            path = os.path.expanduser(path)
            
            # 转换为绝对路径
            path = os.path.abspath(path)
            
            if must_exist:
                if not os.path.exists(path):
                    ui.print_error(f"路径不存在: {path}")
                    if ui.get_confirmation("是否重新输入?", default=True):
                        continue
                    return None
                
                if is_folder and not os.path.isdir(path):
                    ui.print_error(f"这不是一个文件夹: {path}")
                    if ui.get_confirmation("是否重新输入?", default=True):
                        continue
                    return None
                
                if not is_folder and not os.path.isfile(path):
                    ui.print_error(f"这不是一个文件: {path}")
                    if ui.get_confirmation("是否重新输入?", default=True):
                        continue
                    return None
            
            return path
    
    def select_input_file(self, ui, file_pattern: str = '*') -> Optional[str]:
        """
        选择输入文件（支持两种方式）
        
        Args:
            ui: UIHelper实例
            file_pattern: 文件匹配模式
            
        Returns:
            Optional[str]: 选中的文件路径，取消则返回None
        """
        # 获取可用文件夹
        folders = self.get_available_folders()
        
        if not folders:
            ui.print_info("没有可用的默认文件夹，请手动输入路径")
            return self.manual_input_path(ui, must_exist=True)
        
        # 选择方式
        options = [f"从默认文件夹选择"] + [f"{name} ({path})" for name, path in folders] + ["手动输入绝对路径"]
        choice = ui.get_choice("请选择文件路径设置方式:", options, default=0)
        
        if choice == 0:  # 从默认文件夹选择
            # 选择文件夹
            folder_options = [f"{name} ({path})" for name, path in folders]
            folder_choice = ui.get_choice("请选择文件夹:", folder_options)
            return self.select_file_from_folder(ui, folders[folder_choice][1], file_pattern)
        elif choice == len(options) - 1:  # 手动输入
            return self.manual_input_path(ui, must_exist=True)
        else:  # 直接选择某个默认文件夹
            return self.select_file_from_folder(ui, folders[choice - 1][1], file_pattern)
    
    def select_output_path(self, ui, default_name: str = '', is_folder: bool = False) -> Optional[str]:
        """
        选择输出路径
        
        Args:
            ui: UIHelper实例
            default_name: 默认文件名
            is_folder: 是否是文件夹
            
        Returns:
            Optional[str]: 选中的输出路径，取消则返回None
        """
        # 获取可用文件夹
        folders = self.get_available_folders()
        
        options = ["保存到默认文件夹"] + [f"{name} ({path})" for name, path in folders] + ["手动指定绝对路径"]
        choice = ui.get_choice("请选择输出路径设置方式:", options, default=0)
        
        if choice == len(options) - 1:  # 手动指定
            return self.manual_input_path(ui, must_exist=False, is_folder=is_folder)
        else:
            # 选择具体文件夹
            if choice == 0:
                folder_options = [f"{name} ({path})" for name, path in folders]
                folder_choice = ui.get_choice("请选择保存位置:", folder_options)
                base_path = folders[folder_choice][1]
            else:
                base_path = folders[choice - 1][1]
            
            # 输入文件名
            if default_name:
                filename = ui.get_input("请输入文件名", required=True, default=default_name)
            else:
                item_type = "文件夹" if is_folder else "文件"
                filename = ui.get_input(f"请输入{item_type}名称", required=True)
            
            return os.path.join(base_path, filename)
    
    def select_encrypted_file(self, ui) -> Optional[str]:
        """
        选择加密包文件
        
        Args:
            ui: UIHelper实例
            
        Returns:
            Optional[str]: 选中的加密包路径，取消则返回None
        """
        return self.select_input_file(ui, file_pattern='*.7z.enc')
    
    def validate_path(self, path: str, must_exist: bool = True, is_folder: bool = False) -> Tuple[bool, str]:
        """
        验证路径有效性
        
        Args:
            path: 路径
            must_exist: 是否必须存在
            is_folder: 是否是文件夹
            
        Returns:
            Tuple[bool, str]: (是否有效, 错误信息)
        """
        if not path:
            return False, "路径不能为空"
        
        # 展开用户目录
        path = os.path.expanduser(path)
        path = os.path.abspath(path)
        
        if must_exist:
            if not os.path.exists(path):
                return False, f"路径不存在: {path}"
            
            if is_folder:
                if not os.path.isdir(path):
                    return False, f"这不是一个文件夹: {path}"
            else:
                if not os.path.isfile(path):
                    return False, f"这不是一个文件: {path}"
        
        return True, ""
