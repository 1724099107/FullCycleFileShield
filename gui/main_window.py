import sys
from typing import Optional
from PyQt5.QtWidgets import (
    QMainWindow, QTabWidget, QApplication, QAction, QMenu, QMessageBox,
    QStatusBar, QWidget, QVBoxLayout
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from .system_tray import SystemTrayManager

# 导入各个标签页
from .encryption_tab import EncryptionTab
from .decryption_tab import DecryptionTab
from .deletion_tab import DeletionTab
from .about_tab import AboutTab

# 导入CPU环境管理
from utils.gpu_environment import init_gpu_environment, get_compute_device

class MainWindow(QMainWindow):
    """
    主窗口类，包含所有标签页和菜单
    """
    
    def __init__(self):
        """
        初始化主窗口
        """
        super().__init__()
        
        # 系统托盘管理器
        self.system_tray: Optional[SystemTrayManager] = None
        
        # 首先初始化UI，确保窗口能够显示
        print("正在初始化UI...")
        self.init_ui()
        
        # 显示免责声明
        if not self.show_disclaimer():
            sys.exit()
        
        # 初始化CPU环境（在单独的线程中执行，避免阻塞UI）
        import threading
        def init_cpu_in_thread():
            try:
                print("正在初始化CPU环境...")
                cpu_available = init_gpu_environment()
                compute_device = get_compute_device()
                print(f"CPU环境初始化完成，CPU可用: {cpu_available}")
                print(f"当前计算设备: {compute_device}")
            except Exception as e:
                print(f"CPU环境初始化失败: {e}")
                # 即使CPU初始化失败，程序也能继续运行
        
        # 启动线程初始化CPU环境
        cpu_thread = threading.Thread(target=init_cpu_in_thread)
        cpu_thread.daemon = True  # 设为守护线程，主程序退出时自动退出
        cpu_thread.start()
        
        # 初始化系统托盘
        try:
            self.init_system_tray()
        except Exception as e:
            print(f"系统托盘初始化失败: {e}")
            # 即使系统托盘初始化失败，程序也能继续运行
    
    def show_disclaimer(self) -> bool:
        """
        显示免责声明
        
        Returns:
            bool: 用户是否同意免责声明
        """
        disclaimer_text = '''
免责声明

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

4. 更新和支持
   - 开发团队保留随时更新软件的权利
   - 开发团队不保证提供长期技术支持
   - 开发团队不保证修复所有已知漏洞

请仔细阅读以上免责声明。点击"同意"表示您已阅读并接受所有条款。
'''
        
        reply = QMessageBox.question(
            self,
            "免责声明 - FullCycleFileShield",
            disclaimer_text,
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        return reply == QMessageBox.Yes
    
    def init_ui(self) -> None:
        """
        初始化UI组件
        """
        # 设置窗口标题和大小
        self.setWindowTitle("FullCycleFileShield - 文件加密解密工具")
        self.setGeometry(100, 100, 1000, 700)
        
        # 创建标签页控件
        self.tabs = QTabWidget()
        
        # 创建各个标签页
        self.encryption_tab = EncryptionTab()
        self.decryption_tab = DecryptionTab()
        self.deletion_tab = DeletionTab()
        self.about_tab = AboutTab()
        
        # 添加标签页到标签页控件
        self.tabs.addTab(self.encryption_tab, "加密模式")
        self.tabs.addTab(self.decryption_tab, "解密模式")
        self.tabs.addTab(self.deletion_tab, "文件删除")
        self.tabs.addTab(self.about_tab, "关于")
        
        # 设置标签页位置
        self.tabs.setTabPosition(QTabWidget.North)
        
        # 设置标签页形状
        self.tabs.setTabShape(QTabWidget.Rounded)
        
        # 设置中心控件
        self.setCentralWidget(self.tabs)
        
        # 创建菜单栏
        self.create_menu()
        
        # 创建状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("就绪")
        
        # 显示窗口
        self.show()
    
    def create_menu(self) -> None:
        """
        创建菜单栏
        """
        # 创建菜单栏
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu("文件")
        
        # 退出动作
        exit_action = QAction("退出", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 模式菜单
        mode_menu = menubar.addMenu("模式")
        
        # 加密模式动作
        encryption_action = QAction("加密模式", self)
        encryption_action.triggered.connect(lambda: self.tabs.setCurrentIndex(0))
        mode_menu.addAction(encryption_action)
        
        # 解密模式动作
        decryption_action = QAction("解密模式", self)
        decryption_action.triggered.connect(lambda: self.tabs.setCurrentIndex(1))
        mode_menu.addAction(decryption_action)
        
        # 文件删除动作
        deletion_action = QAction("文件删除", self)
        deletion_action.triggered.connect(lambda: self.tabs.setCurrentIndex(2))
        mode_menu.addAction(deletion_action)
        
        # 帮助菜单
        help_menu = menubar.addMenu("帮助")
        
        # 关于动作
        about_action = QAction("关于", self)
        about_action.triggered.connect(lambda: self.tabs.setCurrentIndex(3))
        help_menu.addAction(about_action)
        
        # 帮助文档动作
        help_doc_action = QAction("帮助文档", self)
        help_doc_action.triggered.connect(self.show_help)
        help_menu.addAction(help_doc_action)
    
    def show_help(self) -> None:
        """
        显示帮助文档
        """
        QMessageBox.information(
            self, "帮助文档", 
            "FullCycleFileShield 是一个符合 GB/T39786-2021 第 5 级标准的文件加密解密工具。\n\n" +
            "主要功能：\n" +
            "1. 加密模式：将文件夹加密为加密包\n" +
            "2. 解密模式：将加密包解密为原始文件夹\n" +
            "3. 文件删除：按照 BMB21-2019 标准彻底删除文件\n" +
            "4. 关于：查看软件信息\n\n" +
            "使用方法：\n" +
            "1. 在相应标签页选择操作类型\n" +
            "2. 按照提示设置参数\n" +
            "3. 点击开始按钮执行操作"
        )
    
    def init_system_tray(self) -> None:
        """
        初始化系统托盘
        """
        self.system_tray = SystemTrayManager(self)
        
        # 连接系统托盘信号
        self.system_tray.show_main_window.connect(self.show_main_window_from_tray)
        self.system_tray.exit_application.connect(self.exit_application_from_tray)
        
        # 显示系统托盘
        self.system_tray.show()
    
    def show_main_window_from_tray(self) -> None:
        """
        从系统托盘显示主窗口
        """
        self.show()
        self.raise_()
        self.activateWindow()
    
    def exit_application_from_tray(self) -> None:
        """
        从系统托盘退出应用程序
        """
        self.close()
    
    def closeEvent(self, event) -> None:
        """
        关闭窗口事件处理
        """
        reply = QMessageBox.question(
            self, "退出确认", "确定要退出吗？",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # 关闭系统托盘
            if hasattr(self, 'system_tray') and self.system_tray:
                self.system_tray.shutdown()
            event.accept()
        else:
            event.ignore()

# 主函数
if __name__ == "__main__":
    # 检查是否是测试模式
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--test', action='store_true', help='测试模式，跳过GUI初始化')
    args = parser.parse_args()
    
    if args.test:
        # 测试模式，只初始化CPU环境
        print("测试模式：初始化CPU环境...")
        from utils.gpu_environment import init_gpu_environment, get_compute_device
        cpu_available = init_gpu_environment()
        compute_device = get_compute_device()
        print(f"CPU环境初始化完成，CPU可用: {cpu_available}")
        print(f"当前计算设备: {compute_device}")
        print("测试模式完成")
        sys.exit(0)
    else:
        # 正常模式，启动GUI
        app = QApplication(sys.argv)
        window = MainWindow()
        sys.exit(app.exec_())
