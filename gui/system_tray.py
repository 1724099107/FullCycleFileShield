from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction, QMessageBox
from PyQt5.QtCore import Qt, pyqtSignal, QObject
from PyQt5.QtGui import QIcon, QPixmap
import sys
import os

class SystemTrayManager(QObject):
    """
    系统托盘管理器
    """
    
    # 信号定义
    show_main_window = pyqtSignal()
    exit_application = pyqtSignal()
    
    def __init__(self, parent=None):
        """
        初始化系统托盘管理器
        
        Args:
            parent: 父窗口
        """
        super().__init__(parent)
        self.parent = parent
        self.tray_icon = None
        self.create_system_tray()
    
    def create_system_tray(self):
        """
        创建系统托盘图标
        """
        # 检查系统是否支持系统托盘
        if not QSystemTrayIcon.isSystemTrayAvailable():
            print("系统不支持系统托盘功能，将禁用托盘图标")
            return
        
        try:
            # 创建托盘图标
            self.tray_icon = QSystemTrayIcon(self.parent)
            
            # 设置托盘图标
            icon = self._create_default_icon()
            self.tray_icon.setIcon(icon)
            
            # 设置托盘图标提示
            self.tray_icon.setToolTip("FullCycleFileShield")
            
            # 创建托盘菜单
            self.create_tray_menu()
            
            # 连接信号
            self.tray_icon.activated.connect(self.tray_icon_activated)
        except Exception as e:
            print(f"创建系统托盘失败: {e}")
            self.tray_icon = None
    
    def _create_default_icon(self):
        """
        创建默认托盘图标
        
        Returns:
            QIcon: 默认图标
        """
        # 创建一个简单的图标
        pixmap = QPixmap(64, 64)
        pixmap.fill(Qt.blue)
        
        # 在这里可以添加更复杂的图标创建逻辑
        # 例如使用QPainter绘制FCFS的标志
        
        return QIcon(pixmap)
    
    def create_tray_menu(self):
        """
        创建托盘菜单
        """
        # 创建菜单
        tray_menu = QMenu(self.parent)
        
        # 显示主窗口动作
        show_action = QAction("显示主窗口", self.parent)
        show_action.triggered.connect(self.show_main_window.emit)
        tray_menu.addAction(show_action)
        
        # 添加分隔线
        tray_menu.addSeparator()
        
        # 快速操作子菜单
        quick_actions_menu = QMenu("快速操作", self.parent)
        
        # 快速加密动作
        quick_encrypt_action = QAction("快速加密", self.parent)
        quick_encrypt_action.triggered.connect(self.quick_encrypt)
        quick_actions_menu.addAction(quick_encrypt_action)
        
        # 快速解密动作
        quick_decrypt_action = QAction("快速解密", self.parent)
        quick_decrypt_action.triggered.connect(self.quick_decrypt)
        quick_actions_menu.addAction(quick_decrypt_action)
        
        # 快速删除动作
        quick_delete_action = QAction("快速删除", self.parent)
        quick_delete_action.triggered.connect(self.quick_delete)
        quick_actions_menu.addAction(quick_delete_action)
        
        tray_menu.addMenu(quick_actions_menu)
        
        # 添加分隔线
        tray_menu.addSeparator()
        
        # 监控状态动作
        monitor_status_action = QAction("监控状态", self.parent)
        monitor_status_action.triggered.connect(self.show_monitor_status)
        tray_menu.addAction(monitor_status_action)
        
        # 添加分隔线
        tray_menu.addSeparator()
        
        # 退出动作
        exit_action = QAction("退出", self.parent)
        exit_action.triggered.connect(self.exit_application.emit)
        tray_menu.addAction(exit_action)
        
        # 设置托盘图标菜单
        self.tray_icon.setContextMenu(tray_menu)
    
    def tray_icon_activated(self, reason):
        """
        托盘图标激活事件处理
        
        Args:
            reason: 激活原因
        """
        if reason == QSystemTrayIcon.DoubleClick:
            # 双击显示主窗口
            self.show_main_window.emit()
    
    def show_tray_message(self, title, message, icon=QSystemTrayIcon.Information, duration=3000):
        """
        显示托盘消息
        
        Args:
            title: 消息标题
            message: 消息内容
            icon: 消息图标
            duration: 显示时长（毫秒）
        """
        if self.tray_icon:
            self.tray_icon.showMessage(title, message, icon, duration)
    
    def show(self):
        """
        显示托盘图标
        """
        if self.tray_icon:
            self.tray_icon.show()
    
    def hide(self):
        """
        隐藏托盘图标
        """
        if self.tray_icon:
            self.tray_icon.hide()
    
    def quick_encrypt(self):
        """
        快速加密操作
        """
        # 这里可以实现快速加密功能
        # 例如打开文件选择对话框，选择文件后直接加密
        self.show_tray_message(
            "快速加密", 
            "快速加密功能将在主窗口中打开"
        )
        self.show_main_window.emit()
        
        # 可以在这里添加更多逻辑，例如直接跳转到加密标签页
        if hasattr(self.parent, 'tabs'):
            self.parent.tabs.setCurrentIndex(0)  # 假设0是加密标签页的索引
    
    def quick_decrypt(self):
        """
        快速解密操作
        """
        self.show_tray_message(
            "快速解密", 
            "快速解密功能将在主窗口中打开"
        )
        self.show_main_window.emit()
        
        if hasattr(self.parent, 'tabs'):
            self.parent.tabs.setCurrentIndex(1)  # 假设1是解密标签页的索引
    
    def quick_delete(self):
        """
        快速删除操作
        """
        self.show_tray_message(
            "快速删除", 
            "快速删除功能将在主窗口中打开"
        )
        self.show_main_window.emit()
        
        if hasattr(self.parent, 'tabs'):
            self.parent.tabs.setCurrentIndex(2)  # 假设2是删除标签页的索引
    
    def show_monitor_status(self):
        """
        显示监控状态
        """
        self.show_tray_message(
            "监控状态", 
            "监控状态将在主窗口中显示"
        )
        self.show_main_window.emit()
        
        if hasattr(self.parent, 'tabs'):
            self.parent.tabs.setCurrentIndex(3)  # 假设3是监控标签页的索引
    
    def update_tray_icon(self, icon=None):
        """
        更新托盘图标
        
        Args:
            icon: 新图标
        """
        if self.tray_icon:
            if icon:
                self.tray_icon.setIcon(icon)
            else:
                # 使用默认图标
                default_icon = self._create_default_icon()
                self.tray_icon.setIcon(default_icon)
    
    def set_tool_tip(self, tooltip):
        """
        设置托盘图标提示
        
        Args:
            tooltip: 提示文本
        """
        if self.tray_icon:
            self.tray_icon.setToolTip(tooltip)
    
    def is_visible(self):
        """
        检查托盘图标是否可见
        
        Returns:
            bool: 是否可见
        """
        if self.tray_icon:
            return self.tray_icon.isVisible()
        return False
    
    def shutdown(self):
        """
        关闭托盘图标
        """
        if self.tray_icon:
            self.tray_icon.hide()
            self.tray_icon.deleteLater()
            self.tray_icon = None
