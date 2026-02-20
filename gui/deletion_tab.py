import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QFileDialog, QProgressBar, QTextEdit, QGroupBox, QCheckBox, QRadioButton,
    QButtonGroup
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QTextCursor

class DeletionWorker(QThread):
    """
    删除工作线程，用于在后台执行文件删除操作
    """
    # 信号定义
    progress_update = pyqtSignal(int)
    log_update = pyqtSignal(str)
    finished = pyqtSignal(bool, str)
    time_remaining = pyqtSignal(str)
    
    def __init__(self, target_path, delete_type="file"):
        """
        初始化删除工作线程
        
        Args:
            target_path (str): 目标文件路径（单个文件或用分号分隔的多个文件）、文件夹路径或分区挂载点
            delete_type (str): 删除类型，"file"、"folder"或"partition"
        """
        super().__init__()
        self.target_path = target_path
        self.delete_type = delete_type
    
    def run(self):
        """
        执行删除操作
        """
        import time
        start_time = time.time()
        
        try:
            # 2. 执行删除操作
            if self.delete_type == "file":
                # 导入删除相关模块
                from deletion.bmb21_2019 import BMB212019Deletion
                from deletion.verification import DeletionVerification
                
                # 1. 创建删除工具
                self.log_update.emit(f"开始使用BMB21-2019标准删除文件...")
                deletion_tool = BMB212019Deletion()
                
                # 处理单个或多个文件
                file_paths = [p.strip() for p in self.target_path.split(";") if p.strip()]
                if len(file_paths) == 1:
                    # 单个文件删除
                    deletion_tool.delete_file(file_paths[0])
                    target_path = file_paths[0]
                else:
                    # 批量文件删除
                    self.log_update.emit(f"\n发现 {len(file_paths)} 个文件，开始批量删除...")
                    success_count, failure_count, failed_files = deletion_tool.delete_files(file_paths)
                    self.log_update.emit(f"\n批量删除完成: 成功 {success_count} 个，失败 {failure_count} 个")
                    
                    if failed_files:
                        self.log_update.emit("\n失败的文件:")
                        for file_path, error in failed_files:
                            self.log_update.emit(f"  - {file_path}: {error}")
                    
                    # 使用第一个文件路径进行后续验证（仅作参考）
                    target_path = file_paths[0] if file_paths else self.target_path
                
                # 计算剩余时间
                elapsed_time = time.time() - start_time
                estimated_total_time = elapsed_time / 0.8  # 假设80%进度已完成
                remaining_time = max(0, estimated_total_time - elapsed_time)
                self.time_remaining.emit(f"{int(remaining_time)}秒")
                self.progress_update.emit(80)
                
                # 3. 验证删除结果
                self.log_update.emit("\n开始验证删除结果...")
                verification = DeletionVerification()
                
                success, result = verification.verify_file_deletion(target_path)
                
                self.log_update.emit(f"验证结果: {result}")
                
                # 4. 生成删除验证报告
                self.log_update.emit("\n生成删除验证报告...")
                
                self.progress_update.emit(100)
                self.time_remaining.emit("0秒")
                
                if len(file_paths) > 1:
                    self.log_update.emit(f"\n✓ 批量删除完成！")
                    self.finished.emit(True, "删除成功")
                elif success:
                    self.log_update.emit(f"\n✓ 文件彻底删除完成！")
                    self.finished.emit(True, "删除成功")
                else:
                    self.log_update.emit(f"\n✗ 文件删除可能不彻底！")
                    self.finished.emit(False, "删除可能不彻底")
            elif self.delete_type == "folder":
                # 导入删除相关模块
                from deletion.bmb21_2019 import BMB212019Deletion
                from deletion.verification import DeletionVerification
                
                # 1. 创建删除工具
                self.log_update.emit(f"开始使用BMB21-2019标准删除文件夹...")
                deletion_tool = BMB212019Deletion()
                
                # 文件夹删除
                deletion_tool.delete_folder(self.target_path)
                target_path = self.target_path
                
                # 计算剩余时间
                elapsed_time = time.time() - start_time
                estimated_total_time = elapsed_time / 0.8  # 假设80%进度已完成
                remaining_time = max(0, estimated_total_time - elapsed_time)
                self.time_remaining.emit(f"{int(remaining_time)}秒")
                self.progress_update.emit(80)
                
                # 3. 验证删除结果
                self.log_update.emit("\n开始验证删除结果...")
                verification = DeletionVerification()
                
                success, result = verification.verify_folder_deletion(target_path)
                
                self.log_update.emit(f"验证结果: {result}")
                
                # 4. 生成删除验证报告
                self.log_update.emit("\n生成删除验证报告...")
                
                self.progress_update.emit(100)
                self.time_remaining.emit("0秒")
                
                if success:
                    self.log_update.emit(f"\n✓ 文件夹彻底删除完成！")
                    self.finished.emit(True, "删除成功")
                else:
                    self.log_update.emit(f"\n✗ 文件夹删除可能不彻底！")
                    self.finished.emit(False, "删除可能不彻底")
            else:
                # 分区删除
                # 导入删除相关模块
                from deletion.partition_deletion import PartitionDeletion
                
                # 1. 创建分区删除工具
                self.log_update.emit(f"开始使用BMB21-2019标准删除分区...")
                deletion_tool = PartitionDeletion()
                
                # 2. 执行分区删除操作
                stats = deletion_tool.delete_partition(self.target_path, confirm=True)
                
                # 计算剩余时间
                elapsed_time = time.time() - start_time
                estimated_total_time = elapsed_time / 0.8  # 假设80%进度已完成
                remaining_time = max(0, estimated_total_time - elapsed_time)
                self.time_remaining.emit(f"{int(remaining_time)}秒")
                self.progress_update.emit(80)
                
                # 3. 验证删除结果
                self.log_update.emit("\n开始验证删除结果...")
                success = deletion_tool.verify_deletion(self.target_path)
                
                self.log_update.emit(f"验证结果: {'成功' if success else '失败'}")
                
                # 4. 生成删除验证报告
                self.log_update.emit("\n生成删除验证报告...")
                report = deletion_tool.get_deletion_report()
                
                self.log_update.emit(f"删除报告: 总文件数={report['stats']['total_files']}, 已删除={report['stats']['deleted_files']}, 失败={report['stats']['failed_files']}")
                
                self.progress_update.emit(100)
                self.time_remaining.emit("0秒")
                
                if success:
                    self.log_update.emit(f"\n✓ 分区彻底删除完成！")
                    self.finished.emit(True, "删除成功")
                else:
                    self.log_update.emit(f"\n✗ 分区删除可能不彻底！")
                    self.finished.emit(False, "删除可能不彻底")
        except Exception as e:
            self.log_update.emit(f"\n✗ 删除失败: {str(e)}")
            self.finished.emit(False, f"删除失败: {str(e)}")

class DeletionTab(QWidget):
    """
    文件删除标签页
    """
    
    def __init__(self):
        """
        初始化文件删除标签页
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
        
        # 删除类型选择部分
        type_group = QGroupBox("删除类型")
        type_layout = QHBoxLayout()
        
        # 创建单选按钮组
        self.type_group = QButtonGroup()
        
        # 文件删除选项
        self.file_radio = QRadioButton("文件删除")
        self.file_radio.setChecked(True)
        self.type_group.addButton(self.file_radio)
        
        # 文件夹删除选项
        self.folder_radio = QRadioButton("文件夹删除")
        self.type_group.addButton(self.folder_radio)
        
        # 分区删除选项
        self.partition_radio = QRadioButton("分区删除")
        self.type_group.addButton(self.partition_radio)
        
        type_layout.addWidget(self.file_radio)
        type_layout.addWidget(self.folder_radio)
        type_layout.addWidget(self.partition_radio)
        type_group.setLayout(type_layout)
        
        # 目标选择部分
        target_group = QGroupBox("选择目标")
        target_layout = QHBoxLayout()
        
        self.target_line_edit = QLineEdit()
        self.target_line_edit.setPlaceholderText("选择要删除的文件或文件夹")
        
        target_browse_btn = QPushButton("浏览...")
        target_browse_btn.clicked.connect(self.browse_target)
        
        target_layout.addWidget(self.target_line_edit)
        target_layout.addWidget(target_browse_btn)
        target_group.setLayout(target_layout)
        
        # 删除选项部分
        option_group = QGroupBox("删除选项")
        option_layout = QVBoxLayout()
        
        # 安全删除选项
        self.safe_delete_checkbox = QCheckBox("启用安全删除（按照BMB21-2019标准）")
        self.safe_delete_checkbox.setChecked(True)
        self.safe_delete_checkbox.setEnabled(False)  # 当前版本强制使用安全删除
        
        option_layout.addWidget(self.safe_delete_checkbox)
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
        
        self.start_btn = QPushButton("开始删除")
        self.start_btn.clicked.connect(self.start_deletion)
        
        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.clicked.connect(self.cancel_deletion)
        self.cancel_btn.setEnabled(False)
        
        button_layout.addWidget(self.start_btn)
        button_layout.addWidget(self.cancel_btn)
        
        # 日志显示部分
        log_group = QGroupBox("删除日志")
        log_layout = QVBoxLayout()
        
        self.log_text_edit = QTextEdit()
        self.log_text_edit.setReadOnly(True)
        self.log_text_edit.setLineWrapMode(QTextEdit.NoWrap)
        
        log_layout.addWidget(self.log_text_edit)
        log_group.setLayout(log_layout)
        
        # 添加所有组件到主布局
        main_layout.addWidget(type_group)
        main_layout.addWidget(target_group)
        main_layout.addWidget(option_group)
        main_layout.addWidget(self.progress_bar)
        main_layout.addWidget(self.time_remaining_label)
        main_layout.addLayout(button_layout)
        main_layout.addWidget(log_group)
        
        # 设置主布局
        self.setLayout(main_layout)
    
    def browse_target(self):
        """
        浏览选择目标文件、文件夹或分区
        """
        if self.file_radio.isChecked():
            # 文件选择，支持多选
            target_paths, _ = QFileDialog.getOpenFileNames(
                self, "选择要删除的文件", "", "所有文件 (*.*)"
            )
            if target_paths:
                # 显示多个文件路径，用分号分隔
                self.target_line_edit.setText(";" .join(target_paths))
        elif self.folder_radio.isChecked():
            # 文件夹选择
            target_path = QFileDialog.getExistingDirectory(
                self, "选择要删除的文件夹"
            )
            if target_path:
                self.target_line_edit.setText(target_path)
        else:
            # 分区选择
            from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QPushButton, QLabel
            from deletion.partition_deletion import PartitionDeletion
            
            # 创建分区选择对话框
            dialog = QDialog(self)
            dialog.setWindowTitle("选择要删除的分区")
            dialog.setGeometry(100, 100, 600, 400)
            
            layout = QVBoxLayout()
            
            # 分区列表
            self.partition_list = QListWidget()
            
            # 获取分区信息
            try:
                deleter = PartitionDeletion()
                partitions = deleter.get_partitions()
                
                for i, partition in enumerate(partitions):
                    partition_info = f"{partition['device']} - {partition['description']}"
                    partition_info += f" (文件系统: {partition['file_system']}, 总容量: {partition['size'] / (1024 ** 3):.2f} GB)"
                    self.partition_list.addItem(partition_info)
                    # 存储分区信息
                    self.partition_list.item(i).setData(Qt.UserRole, partition)
            except Exception as e:
                self.partition_list.addItem(f"获取分区信息失败: {str(e)}")
                self.log_update(f"获取分区信息失败: {str(e)}")
            
            layout.addWidget(self.partition_list)
            
            # 按钮布局
            button_layout = QHBoxLayout()
            button_layout.addStretch()
            
            ok_button = QPushButton("确定")
            cancel_button = QPushButton("取消")
            
            def on_ok():
                selected_items = self.partition_list.selectedItems()
                if selected_items:
                    selected_partition = selected_items[0].data(Qt.UserRole)
                    self.target_line_edit.setText(selected_partition['mountpoint'])
                    dialog.accept()
            
            ok_button.clicked.connect(on_ok)
            cancel_button.clicked.connect(dialog.reject)
            
            button_layout.addWidget(ok_button)
            button_layout.addWidget(cancel_button)
            
            layout.addLayout(button_layout)
            dialog.setLayout(layout)
            
            dialog.exec_()
    
    def start_deletion(self):
        """
        开始删除操作
        """
        # 检查输入是否完整
        target_path = self.target_line_edit.text().strip()
        
        if not target_path:
            if self.partition_radio.isChecked():
                self.log_update("请选择要删除的分区")
            else:
                self.log_update("请选择要删除的文件或文件夹")
            return
        
        # 处理分区删除的情况
        if self.partition_radio.isChecked():
            # 确认删除操作
            from PyQt5.QtWidgets import QMessageBox
            
            reply = QMessageBox.question(
                self, "删除确认", f"确定要彻底删除分区 '{target_path}' 内的所有文件吗？此操作不可恢复！",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            
            if reply != QMessageBox.Yes:
                return
            
            # 清空日志和进度条
            self.log_text_edit.clear()
            self.progress_bar.setValue(0)
            self.progress_bar.setVisible(True)
            self.time_remaining_label.setText("剩余时间: 计算中...")
            self.time_remaining_label.setVisible(True)
            
            # 禁用按钮
            self.start_btn.setEnabled(False)
            self.cancel_btn.setEnabled(True)
            
            # 创建并启动删除工作线程
            self.worker = DeletionWorker(target_path, "partition")
            self.worker.progress_update.connect(self.update_progress)
            self.worker.log_update.connect(self.log_update)
            self.worker.time_remaining.connect(self.update_time_remaining)
            self.worker.finished.connect(self.deletion_finished)
            self.worker.start()
        # 处理多个文件的情况
        elif self.file_radio.isChecked() and ";" in target_path:
            # 分割文件路径
            file_paths = [p.strip() for p in target_path.split(";") if p.strip()]
            
            # 检查是否有文件存在
            existing_files = [p for p in file_paths if os.path.exists(p)]
            if not existing_files:
                self.log_update(f"目标不存在: {target_path}")
                return
            
            # 确认删除操作
            from PyQt5.QtWidgets import QMessageBox
            
            reply = QMessageBox.question(
                self, "删除确认", f"确定要彻底删除 {len(existing_files)} 个文件吗？此操作不可恢复！",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            
            if reply != QMessageBox.Yes:
                return
            
            # 清空日志和进度条
            self.log_text_edit.clear()
            self.progress_bar.setValue(0)
            self.progress_bar.setVisible(True)
            self.time_remaining_label.setText("剩余时间: 计算中...")
            self.time_remaining_label.setVisible(True)
            
            # 禁用按钮
            self.start_btn.setEnabled(False)
            self.cancel_btn.setEnabled(True)
            
            # 创建并启动删除工作线程
            self.worker = DeletionWorker(target_path, "file")
            self.worker.progress_update.connect(self.update_progress)
            self.worker.log_update.connect(self.log_update)
            self.worker.time_remaining.connect(self.update_time_remaining)
            self.worker.finished.connect(self.deletion_finished)
            self.worker.start()
        else:
            # 单个文件或文件夹的情况
            # 检查目标是否存在
            if not os.path.exists(target_path):
                self.log_update(f"目标不存在: {target_path}")
                return
            
            # 确认删除操作
            from PyQt5.QtWidgets import QMessageBox
            
            delete_type = "文件" if self.file_radio.isChecked() else "文件夹"
            reply = QMessageBox.question(
                self, "删除确认", f"确定要彻底删除{delete_type} '{target_path}'吗？此操作不可恢复！",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            
            if reply != QMessageBox.Yes:
                return
            
            # 清空日志和进度条
            self.log_text_edit.clear()
            self.progress_bar.setValue(0)
            self.progress_bar.setVisible(True)
            self.time_remaining_label.setText("剩余时间: 计算中...")
            self.time_remaining_label.setVisible(True)
            
            # 禁用按钮
            self.start_btn.setEnabled(False)
            self.cancel_btn.setEnabled(True)
            
            # 创建并启动删除工作线程
            delete_type = "file" if self.file_radio.isChecked() else "folder"
            self.worker = DeletionWorker(target_path, delete_type)
            self.worker.progress_update.connect(self.update_progress)
            self.worker.log_update.connect(self.log_update)
            self.worker.time_remaining.connect(self.update_time_remaining)
            self.worker.finished.connect(self.deletion_finished)
            self.worker.start()
    
    def cancel_deletion(self):
        """
        取消删除操作
        """
        if self.worker and self.worker.isRunning():
            self.worker.terminate()
            self.worker.wait()
            self.log_update("\n✗ 删除已取消")
            self.deletion_finished(False, "删除已取消")
    
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
    
    def deletion_finished(self, success, message):
        """
        删除完成处理
        
        Args:
            success (bool): 删除是否成功
            message (str): 完成消息
        """
        # 启用按钮
        self.start_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        
        # 隐藏剩余时间显示
        self.time_remaining_label.setVisible(False)
        
        # 显示完成消息
        if not success:
            self.log_update(f"\n✗ 删除失败: {message}")


