import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QFileDialog, QProgressBar, QTextEdit, QGroupBox, QCheckBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QTextCursor

class DecryptionWorker(QThread):
    """
    解密工作线程，用于在后台执行解密操作
    """
    # 信号定义
    progress_update = pyqtSignal(int)
    log_update = pyqtSignal(str)
    finished = pyqtSignal(bool, str)
    time_remaining = pyqtSignal(str)
    
    def __init__(self, encrypted_file, output_folder, master_key, delete_encrypted=False):
        """
        初始化解密工作线程
        
        Args:
            encrypted_file (str): 加密包路径
            output_folder (str): 输出文件夹路径
            master_key (bytes): 主密钥
            delete_encrypted (bool): 是否删除加密包
        """
        super().__init__()
        self.encrypted_file = encrypted_file
        self.output_folder = output_folder
        self.master_key = master_key
        self.delete_encrypted = delete_encrypted
    
    def run(self):
        """
        执行解密操作
        """
        import time
        start_time = time.time()
        
        try:
            # 导入解密相关模块
            from decryption.pre_check import DecryptionPreCheck
            from decryption.hybrid_decryption import HybridDecryption
            from decryption.decompression import Decompression
            from decryption.cleanup import DecryptionCleanup
            
            # 1. 解密前预检
            self.log_update.emit("开始解密前预检...")
            pre_check = DecryptionPreCheck()
            if not pre_check.run_all_checks(self.encrypted_file, self.master_key):
                self.finished.emit(False, "解密前预检失败")
                return
            
            # 2. 混合解密
            self.log_update.emit("\n开始混合解密...")
            hybrid_decryption = HybridDecryption()
            decrypted_file, sha512_hash, sm3_hash = hybrid_decryption.decrypt(
                self.encrypted_file, self.master_key
            )
            self.progress_update.emit(50)
            
            # 计算剩余时间
            elapsed_time = time.time() - start_time
            estimated_total_time = elapsed_time / 0.5  # 假设50%进度已完成
            remaining_time = max(0, estimated_total_time - elapsed_time)
            self.time_remaining.emit(f"{int(remaining_time)}秒")
            
            # 3. 7Z解压
            self.log_update.emit("\n开始7Z解压...")
            decompression = Decompression()
            
            # 定义进度回调函数
            def progress_callback(progress):
                self.progress_update.emit(progress)
            
            # 定义时间回调函数
            def time_callback(time_str):
                self.time_remaining.emit(time_str)
            
            decompression.decompress(
                decrypted_file, 
                self.output_folder, 
                progress_callback=progress_callback, 
                time_callback=time_callback
            )
            
            # 计算剩余时间
            elapsed_time = time.time() - start_time
            estimated_total_time = elapsed_time / 0.9  # 假设90%进度已完成
            remaining_time = max(0, estimated_total_time - elapsed_time)
            self.time_remaining.emit(f"{int(remaining_time)}秒")
            
            # 4. 清理操作
            self.log_update.emit("\n开始清理操作...")
            cleanup = DecryptionCleanup()
            cleanup.delete_temp_file(decrypted_file)
            
            # 如果需要删除加密包
            if self.delete_encrypted:
                cleanup.delete_encrypted_file(self.encrypted_file)
            
            cleanup.clear_memory()
            
            self.progress_update.emit(100)
            self.time_remaining.emit("0秒")
            self.log_update.emit(f"\n✓ 解密完成！输出文件夹: {self.output_folder}")
            self.log_update.emit(f"SHA-512: {sha512_hash}")
            self.log_update.emit(f"SM3: {sm3_hash}")
            
            self.finished.emit(True, "解密成功")
        except Exception as e:
            self.log_update.emit(f"\n✗ 解密失败: {str(e)}")
            self.finished.emit(False, f"解密失败: {str(e)}")

class DecryptionTab(QWidget):
    """
    解密模式标签页
    """
    
    def __init__(self):
        """
        初始化解密标签页
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
        
        # 加密包选择部分
        encrypted_file_group = QGroupBox("选择加密包")
        encrypted_file_layout = QHBoxLayout()
        
        self.encrypted_file_line_edit = QLineEdit()
        self.encrypted_file_line_edit.setPlaceholderText("选择加密包")
        encrypted_file_browse_btn = QPushButton("浏览...")
        encrypted_file_browse_btn.clicked.connect(self.browse_encrypted_file)
        
        encrypted_file_layout.addWidget(self.encrypted_file_line_edit)
        encrypted_file_layout.addWidget(encrypted_file_browse_btn)
        encrypted_file_group.setLayout(encrypted_file_layout)
        
        # 输出文件夹部分
        output_folder_group = QGroupBox("设置输出文件夹")
        output_folder_layout = QHBoxLayout()
        
        self.output_folder_line_edit = QLineEdit()
        self.output_folder_line_edit.setPlaceholderText("设置输出文件夹")
        output_folder_browse_btn = QPushButton("浏览...")
        output_folder_browse_btn.clicked.connect(self.browse_output_folder)
        
        output_folder_layout.addWidget(self.output_folder_line_edit)
        output_folder_layout.addWidget(output_folder_browse_btn)
        output_folder_group.setLayout(output_folder_layout)
        
        # 主密钥部分
        key_group = QGroupBox("主密钥设置")
        key_layout = QVBoxLayout()
        
        # 密钥输入布局
        key_input_layout = QHBoxLayout()
        self.key_line_edit = QLineEdit()
        self.key_line_edit.setPlaceholderText("输入主密钥")
        self.key_line_edit.setEchoMode(QLineEdit.Password)
        
        # 复制密钥按钮（保留，方便用户粘贴密钥）
        self.copy_key_btn = QPushButton("粘贴密钥")
        self.copy_key_btn.clicked.connect(self.paste_key)
        
        key_input_layout.addWidget(self.key_line_edit)
        key_input_layout.addWidget(self.copy_key_btn)
        
        # 密钥输入提示
        self.key_info_label = QLabel("请输入加密时生成的主密钥")
        self.key_info_label.setAlignment(Qt.AlignCenter)
        self.key_info_label.setStyleSheet("QLabel { color: #666666; }")
        
        key_layout.addLayout(key_input_layout)
        key_layout.addWidget(self.key_info_label)
        key_group.setLayout(key_layout)
        
        # 解密选项部分
        option_group = QGroupBox("解密选项")
        option_layout = QVBoxLayout()
        
        # 删除加密包选项
        self.delete_encrypted_checkbox = QCheckBox("解密完成后删除加密包")
        self.delete_encrypted_checkbox.setChecked(False)
        
        option_layout.addWidget(self.delete_encrypted_checkbox)
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
        
        self.start_btn = QPushButton("开始解密")
        self.start_btn.clicked.connect(self.start_decryption)
        
        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.clicked.connect(self.cancel_decryption)
        self.cancel_btn.setEnabled(False)
        
        button_layout.addWidget(self.start_btn)
        button_layout.addWidget(self.cancel_btn)
        
        # 日志显示部分
        log_group = QGroupBox("解密日志")
        log_layout = QVBoxLayout()
        
        self.log_text_edit = QTextEdit()
        self.log_text_edit.setReadOnly(True)
        self.log_text_edit.setLineWrapMode(QTextEdit.NoWrap)
        
        log_layout.addWidget(self.log_text_edit)
        log_group.setLayout(log_layout)
        
        # 添加所有组件到主布局
        main_layout.addWidget(encrypted_file_group)
        main_layout.addWidget(output_folder_group)
        main_layout.addWidget(key_group)
        main_layout.addWidget(option_group)
        main_layout.addWidget(self.progress_bar)
        main_layout.addWidget(self.time_remaining_label)
        main_layout.addLayout(button_layout)
        main_layout.addWidget(log_group)
        
        # 设置主布局
        self.setLayout(main_layout)
    
    def browse_encrypted_file(self):
        """
        浏览选择加密包
        """
        encrypted_file, _ = QFileDialog.getOpenFileName(
            self, "选择加密包", "", "加密包 (*.7z.enc)"
        )
        if encrypted_file:
            self.encrypted_file_line_edit.setText(encrypted_file)
    
    def browse_output_folder(self):
        """
        浏览选择输出文件夹
        """
        output_folder = QFileDialog.getExistingDirectory(self, "选择输出文件夹")
        if output_folder:
            self.output_folder_line_edit.setText(output_folder)
    
    def paste_key(self):
        """
        从剪贴板粘贴密钥
        """
        from PyQt5.QtGui import QClipboard
        from PyQt5.QtWidgets import QApplication
        
        clipboard = QApplication.clipboard()
        key = clipboard.text().strip()
        if key:
            self.key_line_edit.setText(key)
            self.log_update("密钥已从剪贴板粘贴")
        else:
            self.log_update("剪贴板中没有可用的密钥")
    
    def start_decryption(self):
        """
        开始解密操作
        """
        # 检查输入是否完整
        encrypted_file = self.encrypted_file_line_edit.text().strip()
        output_folder = self.output_folder_line_edit.text().strip()
        master_key = self.key_line_edit.text().strip()
        
        if not encrypted_file:
            self.log_update("请选择加密包")
            return
        
        if not output_folder:
            # 如果未指定输出文件夹，使用默认路径
            output_folder = encrypted_file + "_decrypted"
        
        if not master_key:
            self.log_update("请输入主密钥")
            return
        
        # 将主密钥转换为bytes
        master_key_bytes = master_key.encode('utf-8')
        
        # 获取解密选项
        delete_encrypted = self.delete_encrypted_checkbox.isChecked()
        
        # 清空日志和进度条
        self.log_text_edit.clear()
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
        self.time_remaining_label.setText("剩余时间: 计算中...")
        self.time_remaining_label.setVisible(True)
        
        # 禁用按钮
        self.start_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        
        # 创建并启动解密工作线程
        self.worker = DecryptionWorker(encrypted_file, output_folder, master_key_bytes, delete_encrypted)
        self.worker.progress_update.connect(self.update_progress)
        self.worker.log_update.connect(self.log_update)
        self.worker.time_remaining.connect(self.update_time_remaining)
        self.worker.finished.connect(self.decryption_finished)
        self.worker.start()
    
    def cancel_decryption(self):
        """
        取消解密操作
        """
        if self.worker and self.worker.isRunning():
            self.worker.terminate()
            self.worker.wait()
            self.log_update("\n✗ 解密已取消")
            self.decryption_finished(False, "解密已取消")
    
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
    
    def decryption_finished(self, success, message):
        """
        解密完成处理
        
        Args:
            success (bool): 解密是否成功
            message (str): 完成消息
        """
        # 启用按钮
        self.start_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        
        # 隐藏剩余时间显示
        self.time_remaining_label.setVisible(False)
        
        # 如果解密成功，清空输入框
        if success:
            self.key_line_edit.clear()
        
        # 显示完成消息
        if not success:
            self.log_update(f"\n✗ 解密失败: {message}")
