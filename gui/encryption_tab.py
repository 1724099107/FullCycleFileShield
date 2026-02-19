import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QFileDialog, QProgressBar, QTextEdit, QGroupBox, QCheckBox, QComboBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QTextCursor

class EncryptionWorker(QThread):
    """
    加密工作线程，用于在后台执行加密操作
    """
    # 信号定义
    progress_update = pyqtSignal(int)
    log_update = pyqtSignal(str)
    finished = pyqtSignal(bool, str)
    time_remaining = pyqtSignal(str)
    
    def __init__(self, input_path, output_path, master_key, delete_original=False, is_file_list=False):
        """
        初始化加密工作线程
        
        Args:
            input_path (str or list): 待加密文件夹路径、单个文件路径或文件列表
            output_path (str): 输出加密包路径
            master_key (bytes): 主密钥
            delete_original (bool): 是否删除原始文件/文件夹
            is_file_list (bool): 是否为文件列表
        """
        super().__init__()
        self.input_path = input_path
        self.output_path = output_path
        self.master_key = master_key
        self.delete_original = delete_original
        self.is_file_list = is_file_list
    
    def run(self):
        """
        执行加密操作
        """
        import time
        start_time = time.time()
        
        try:
            # 导入加密相关模块
            from encryption.pre_check import EncryptionPreCheck
            from encryption.compression import Compression
            from encryption.hybrid_encryption import HybridEncryption
            from encryption.cleanup import EncryptionCleanup
            
            # 1. 加密前预检
            self.log_update.emit("开始加密前预检...")
            pre_check = EncryptionPreCheck()
            
            # 针对不同类型的输入执行预检
            if isinstance(self.input_path, list):
                # 对于文件列表，分别检查每个文件
                for path in self.input_path:
                    if not pre_check.run_all_checks(path):
                        # 将具体错误信息传递给用户
                        error_msg = f"加密前预检失败: {path} - " + "; ".join(pre_check.errors)
                        self.finished.emit(False, error_msg)
                        return
            else:
                # 对于单个文件或文件夹
                if not pre_check.run_all_checks(self.input_path):
                    # 将具体错误信息传递给用户
                    error_msg = "加密前预检失败 - " + "; ".join(pre_check.errors)
                    self.finished.emit(False, error_msg)
                    return
            
            # 2. 7Z压缩
            self.log_update.emit("\n开始7Z压缩...")
            compression = Compression()
            
            # 定义进度回调函数
            def progress_callback(progress):
                self.progress_update.emit(progress)
            
            # 定义时间回调函数
            def time_callback(time_str):
                self.time_remaining.emit(time_str)
            
            compressed_file, sha512_hash, sm3_hash = compression.compress(
                self.input_path, 
                progress_callback=progress_callback, 
                time_callback=time_callback
            )
            
            # 计算剩余时间
            elapsed_time = time.time() - start_time
            estimated_total_time = elapsed_time / 0.25  # 假设25%进度已完成
            remaining_time = max(0, estimated_total_time - elapsed_time)
            self.time_remaining.emit(f"{int(remaining_time)}秒")
            
            # 3. 混合加密
            self.log_update.emit("\n开始混合加密...")
            hybrid_encryption = HybridEncryption()
            encrypted_file, _, _ = hybrid_encryption.encrypt(compressed_file, self.master_key, self.output_path, sha512_hash, sm3_hash)
            self.progress_update.emit(75)
            
            # 计算剩余时间
            elapsed_time = time.time() - start_time
            estimated_total_time = elapsed_time / 0.75  # 假设75%进度已完成
            remaining_time = max(0, estimated_total_time - elapsed_time)
            self.time_remaining.emit(f"{int(remaining_time)}秒")
            
            # 4. 清理操作
            self.log_update.emit("\n开始清理操作...")
            cleanup = EncryptionCleanup()
            cleanup.delete_temp_file(compressed_file)
            
            # 如果需要删除原始文件/文件夹
            if self.delete_original:
                if isinstance(self.input_path, list):
                    # 删除文件列表中的所有文件/文件夹
                    for path in self.input_path:
                        if os.path.isfile(path):
                            cleanup.delete_temp_file(path)
                        else:
                            cleanup.delete_original_folder(path)
                else:
                    # 删除单个文件或文件夹
                    if os.path.isfile(self.input_path):
                        cleanup.delete_temp_file(self.input_path)
                    else:
                        cleanup.delete_original_folder(self.input_path)
            
            cleanup.clear_memory()
            
            self.progress_update.emit(100)
            self.time_remaining.emit("0秒")
            self.log_update.emit(f"\n✓ 加密完成！加密包路径: {encrypted_file}")
            self.log_update.emit(f"SHA-512: {sha512_hash}")
            self.log_update.emit(f"SM3: {sm3_hash}")
            
            self.finished.emit(True, "加密成功")
        except Exception as e:
            self.log_update.emit(f"\n✗ 加密失败: {str(e)}")
            self.finished.emit(False, f"加密失败: {str(e)}")

class EncryptionTab(QWidget):
    """
    加密模式标签页
    """
    
    def __init__(self):
        """
        初始化加密标签页
        """
        super().__init__()
        self.init_ui()
        self.worker = None
    
    def init_ui(self):
        """
        初始化UI组件
        """
        # 创建主布局
        main_layout = QVBoxLayout()
        
        # 输入选择部分
        input_group = QGroupBox("选择待加密内容")
        input_layout = QVBoxLayout()
        
        # 文件/文件夹路径显示
        self.input_line_edit = QLineEdit()
        self.input_line_edit.setPlaceholderText("选择待加密的文件或文件夹")
        
        # 浏览按钮布局
        browse_layout = QHBoxLayout()
        file_browse_btn = QPushButton("选择文件")
        file_browse_btn.clicked.connect(self.browse_files)
        
        files_browse_btn = QPushButton("选择多个文件")
        files_browse_btn.clicked.connect(self.browse_multiple_files)
        
        folder_browse_btn = QPushButton("选择文件夹")
        folder_browse_btn.clicked.connect(self.browse_folder)
        
        browse_layout.addWidget(file_browse_btn)
        browse_layout.addWidget(files_browse_btn)
        browse_layout.addWidget(folder_browse_btn)
        
        input_layout.addWidget(self.input_line_edit)
        input_layout.addLayout(browse_layout)
        input_group.setLayout(input_layout)
        
        # 输出路径部分
        output_group = QGroupBox("设置输出路径")
        output_layout = QHBoxLayout()
        
        self.output_line_edit = QLineEdit()
        self.output_line_edit.setPlaceholderText("设置输出加密包路径")
        output_browse_btn = QPushButton("浏览...")
        output_browse_btn.clicked.connect(self.browse_output)
        
        output_layout.addWidget(self.output_line_edit)
        output_layout.addWidget(output_browse_btn)
        output_group.setLayout(output_layout)
        
        # 主密钥部分
        key_group = QGroupBox("主密钥设置")
        key_layout = QVBoxLayout()
        
        # 密钥生成说明
        self.key_info_label = QLabel("密钥将由系统自动生成，加密完成后显示")
        self.key_info_label.setAlignment(Qt.AlignCenter)
        self.key_info_label.setWordWrap(True)
        
        # 复制密钥按钮（初始隐藏）
        self.copy_key_btn = QPushButton("复制密钥")
        self.copy_key_btn.clicked.connect(self.copy_generated_key)
        self.copy_key_btn.setVisible(False)  # 初始隐藏
        
        key_layout.addWidget(self.key_info_label)
        key_layout.addWidget(self.copy_key_btn)
        key_group.setLayout(key_layout)
        
        # 加密选项部分
        option_group = QGroupBox("加密选项")
        option_layout = QVBoxLayout()
        
        # 删除原始文件夹选项
        self.delete_original_checkbox = QCheckBox("加密完成后删除原始文件夹")
        self.delete_original_checkbox.setChecked(False)
        
        # 压缩级别选择
        compression_layout = QHBoxLayout()
        compression_label = QLabel("压缩级别:")
        self.compression_combo = QComboBox()
        self.compression_combo.addItems(["1 - 最低", "2", "3", "4", "5 - 中等", "6", "7", "8", "9 - 最高"])
        self.compression_combo.setCurrentIndex(8)  # 默认最高压缩级别
        compression_layout.addWidget(compression_label)
        compression_layout.addWidget(self.compression_combo)
        compression_layout.addStretch()
        
        option_layout.addWidget(self.delete_original_checkbox)
        option_layout.addLayout(compression_layout)
        option_group.setLayout(option_layout)
        
        # 进度条部分
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        
        # 剩余时间显示
        self.time_remaining_label = QLabel("剩余时间: 计算中...")
        self.time_remaining_label.setVisible(False)
        
        # 按钮部分
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.start_btn = QPushButton("开始加密")
        self.start_btn.clicked.connect(self.start_encryption)
        
        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.clicked.connect(self.cancel_encryption)
        self.cancel_btn.setEnabled(False)
        
        button_layout.addWidget(self.start_btn)
        button_layout.addWidget(self.cancel_btn)
        
        # 日志显示部分
        log_group = QGroupBox("加密日志")
        log_layout = QVBoxLayout()
        
        self.log_text_edit = QTextEdit()
        self.log_text_edit.setReadOnly(True)
        self.log_text_edit.setLineWrapMode(QTextEdit.NoWrap)
        
        log_layout.addWidget(self.log_text_edit)
        log_group.setLayout(log_layout)
        
        # 添加所有组件到主布局
        main_layout.addWidget(input_group)
        main_layout.addWidget(output_group)
        main_layout.addWidget(key_group)
        main_layout.addWidget(option_group)
        main_layout.addWidget(self.progress_bar)
        main_layout.addWidget(self.time_remaining_label)
        main_layout.addLayout(button_layout)
        main_layout.addWidget(log_group)
        
        # 初始化输入类型标记
        self.is_file_list = False
        
        # 设置主布局
        self.setLayout(main_layout)
    
    def browse_files(self):
        """
        浏览选择单个待加密文件
        """
        file_path, _ = QFileDialog.getOpenFileName(self, "选择待加密文件")
        if file_path:
            self.input_line_edit.setText(file_path)
            self.is_file_list = False
            # 清除可能存在的文件列表
            if hasattr(self, 'file_list'):
                delattr(self, 'file_list')
    
    def browse_multiple_files(self):
        """
        浏览选择多个待加密文件
        """
        file_paths, _ = QFileDialog.getOpenFileNames(self, "选择多个待加密文件")
        if file_paths:
            self.input_line_edit.setText(f"{len(file_paths)} 个文件")
            # 存储完整的文件列表
            self.file_list = file_paths
            self.is_file_list = True
    
    def browse_folder(self):
        """
        浏览选择待加密文件夹
        """
        folder_path = QFileDialog.getExistingDirectory(self, "选择待加密文件夹")
        if folder_path:
            self.input_line_edit.setText(folder_path)
            self.is_file_list = False
            # 清除可能存在的文件列表
            if hasattr(self, 'file_list'):
                delattr(self, 'file_list')
    
    def browse_output(self):
        """
        浏览选择输出加密包路径
        """
        output_path, _ = QFileDialog.getSaveFileName(
            self, "保存加密包", "", "加密包 (*.7z.enc)"
        )
        if output_path:
            if not output_path.endswith(".7z.enc"):
                output_path += ".7z.enc"
            self.output_line_edit.setText(output_path)
    

    
    def start_encryption(self):
        """
        开始加密操作
        """
        # 检查输入是否完整
        input_text = self.input_line_edit.text().strip()
        output_path = self.output_line_edit.text().strip()
        
        if not input_text:
            self.log_update("请选择待加密的文件或文件夹")
            return
        
        # 确定输入路径
        if self.is_file_list:
            # 使用存储的文件列表，确保file_list属性存在
            if hasattr(self, 'file_list'):
                input_path = self.file_list
            else:
                self.log_update("错误：文件列表不可用")
                return
        else:
            # 使用单行输入的路径
            input_path = input_text
        
        # 如果未指定输出路径，生成默认路径
        if not output_path:
            if isinstance(input_path, list):
                # 对于文件列表，使用第一个文件的目录作为基础
                output_path = os.path.join(os.path.dirname(input_path[0]), "files.7z.enc")
            else:
                # 对于单个文件或文件夹，使用其名称作为基础
                output_path = input_path + ".7z.enc"
        
        # 自动生成随机密钥，不再要求用户输入
        import secrets
        import string
        
        # 生成32位随机密钥，包含大小写字母、数字和特殊字符
        alphabet = string.ascii_letters + string.digits + string.punctuation
        self.generated_key = ''.join(secrets.choice(alphabet) for _ in range(32))
        
        # 将主密钥转换为bytes
        master_key_bytes = self.generated_key.encode('utf-8')
        
        # 获取加密选项
        delete_original = self.delete_original_checkbox.isChecked()
        
        # 清空日志和进度条
        self.log_text_edit.clear()
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
        self.time_remaining_label.setText("剩余时间: 计算中...")
        self.time_remaining_label.setVisible(True)
        
        # 禁用按钮
        self.start_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        
        # 创建并启动加密工作线程
        self.worker = EncryptionWorker(input_path, output_path, master_key_bytes, delete_original, self.is_file_list)
        self.worker.progress_update.connect(self.update_progress)
        self.worker.log_update.connect(self.log_update)
        self.worker.time_remaining.connect(self.update_time_remaining)
        self.worker.finished.connect(self.encryption_finished)
        self.worker.start()
    
    def cancel_encryption(self):
        """
        取消加密操作
        """
        if self.worker and self.worker.isRunning():
            self.worker.terminate()
            self.worker.wait()
            self.log_update("\n✗ 加密已取消")
            self.encryption_finished(False, "加密已取消")
    
    def update_progress(self, value):
        """
        更新进度条
        
        Args:
            value (int): 进度值（0-100）
        """
        self.progress_bar.setValue(value)
    
    def update_time_remaining(self, time_str):
        """
        更新剩余时间显示
        
        Args:
            time_str (str): 剩余时间字符串
        """
        self.time_remaining_label.setText(f"剩余时间: {time_str}")
    
    def log_update(self, message):
        """
        更新日志显示
        
        Args:
            message (str): 日志消息
        """
        self.log_text_edit.append(message)
        # 自动滚动到底部
        cursor = self.log_text_edit.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.log_text_edit.setTextCursor(cursor)
    
    def copy_generated_key(self):
        """
        复制生成的密钥到剪贴板，只能复制一次
        """
        if hasattr(self, 'generated_key') and self.generated_key:
            from PyQt5.QtGui import QClipboard
            from PyQt5.QtWidgets import QApplication
            
            clipboard = QApplication.clipboard()
            clipboard.setText(self.generated_key)
            self.log_update("✓ 密钥已复制到剪贴板")
            
            # 复制后立即清空密钥，确保只能复制一次
            self.generated_key = None
            # 隐藏复制密钥按钮
            self.copy_key_btn.setVisible(False)
            # 更新提示信息
            self.key_info_label.setText("密钥已复制并清理，无法再次复制")
        else:
            self.log_update("✗ 密钥已被清理，无法复制")
            # 隐藏复制密钥按钮
            self.copy_key_btn.setVisible(False)
            # 更新提示信息
            self.key_info_label.setText("密钥已被清理，无法再次复制")
    
    def encryption_finished(self, success, message):
        """
        加密完成处理
        
        Args:
            success (bool): 加密是否成功
            message (str): 完成消息
        """
        # 启用按钮
        self.start_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        
        # 隐藏剩余时间显示
        self.time_remaining_label.setVisible(False)
        
        # 显示完成消息
        if success:
            # 加密成功，显示生成的密钥
            self.log_update(f"\n✓ 加密完成！")
            self.log_update(f"\n=== 请妥善保存以下主密钥，解密时需要使用 ===")
            self.log_update(f"主密钥: {self.generated_key}")
            self.log_update(f"=======================")
            self.log_update(f"\n⚠️  密钥仅显示一次，复制后将立即清理！")
            
            # 显示复制密钥按钮，用户手动复制
            self.copy_key_btn.setVisible(True)
            # 更新提示信息
            self.key_info_label.setText("点击'复制密钥'按钮保存密钥，复制后将立即清理")
        else:
            self.log_update(f"\n✗ 加密失败: {message}")
            # 隐藏复制密钥按钮
            self.copy_key_btn.setVisible(False)
            # 清空生成的密钥，释放内存
            if hasattr(self, 'generated_key'):
                self.generated_key = None
            # 更新提示信息
            self.key_info_label.setText("密钥将由系统自动生成，加密完成后显示")
