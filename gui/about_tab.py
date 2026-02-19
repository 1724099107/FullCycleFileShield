from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QGroupBox, QGridLayout,
    QTextBrowser
)
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QFont, QDesktopServices

class AboutTab(QWidget):
    """
    关于标签页，用于显示软件信息
    """
    
    def __init__(self):
        """
        初始化关于标签页
        """
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        """
        初始化UI组件
        """
        # 创建主布局
        main_layout = QVBoxLayout()
        
        # 软件信息部分
        info_group = QGroupBox("软件信息")
        info_layout = QGridLayout()
        
        # 软件名称
        name_label = QLabel("软件名称:")
        name_value = QLabel("FullCycleFileShield")
        name_value.setFont(QFont("Arial", 12, QFont.Bold))
        
        # 版本号
        version_label = QLabel("版本:")
        version_value = QLabel("1.0.3")
        
        # 作者
        author_label = QLabel("作者:")
        author_value = QLabel("陈修祺(ChenXiuQi)（个人）")
        
        # 版权信息
        copyright_label = QLabel("版权:")
        copyright_value = QLabel("© 2026 陈修祺(ChenXiuQi)（个人）. All rights reserved.")
        
        # 合规标准
        compliance_label = QLabel("合规标准:")
        compliance_value = QLabel("GB/T39786-2021 第5级, BMB21-2019")
        compliance_value.setToolTip("符合国家密码管理局发布的密码应用安全性评估标准")
        
        # 添加到网格布局
        info_layout.addWidget(name_label, 0, 0, Qt.AlignRight)
        info_layout.addWidget(name_value, 0, 1, Qt.AlignLeft)
        info_layout.addWidget(version_label, 1, 0, Qt.AlignRight)
        info_layout.addWidget(version_value, 1, 1, Qt.AlignLeft)
        info_layout.addWidget(author_label, 2, 0, Qt.AlignRight)
        info_layout.addWidget(author_value, 2, 1, Qt.AlignLeft)
        info_layout.addWidget(copyright_label, 3, 0, Qt.AlignRight)
        info_layout.addWidget(copyright_value, 3, 1, Qt.AlignLeft)
        info_layout.addWidget(compliance_label, 4, 0, Qt.AlignRight)
        info_layout.addWidget(compliance_value, 4, 1, Qt.AlignLeft)
        
        info_group.setLayout(info_layout)
        
        # 软件描述部分
        description_group = QGroupBox("软件描述")
        description_layout = QVBoxLayout()
        
        description = QTextBrowser()
        description.setHtml("""
            <p>FullCycleFileShield 是一款符合 GB/T39786-2021 第5级标准的文件加密解密工具，
            采用三层加密架构，结合了量子密钥替代方案和抗量子算法，
            提供了高安全性的文件加密、解密和彻底删除功能。</p>
            <p>主要功能：</p>
            <ul>
                <li>符合国家标准的混合加密架构</li>
                <li>基于BMB21-2019标准的文件彻底删除</li>
                <li>7Z固实压缩和高压缩级别</li>
                <li>支持GUI和命令行双模式</li>
                <li>详细的日志记录和报告生成</li>
                <li>自定义程度高的设置选项</li>
            </ul>
            <p>应用场景：</p>
            <ul>
                <li>敏感数据的安全存储和传输</li>
                <li>符合合规要求的文件处理</li>
                <li>防止数据泄露和恢复</li>
                <li>企业级文件加密解决方案</li>
            </ul>
        """)
        description.setReadOnly(True)
        description_layout.addWidget(description)
        description_group.setLayout(description_layout)
        
        # 技术支持部分
        support_group = QGroupBox("技术支持")
        support_layout = QVBoxLayout()
        
        support_text = QLabel(
            "如果您在使用过程中遇到问题，欢迎联系我们的技术支持团队。\n\n" +
            "邮箱: support@fcfs.free.nf\n" +
            "网站: http://fcfs.free.nf\n" +
            "文档: http://fcfs.free.nf/docs"
        )
        support_text.setAlignment(Qt.AlignCenter)
        support_text.setWordWrap(True)
        
        # 访问官网按钮
        visit_website_btn = QPushButton("访问官网")
        visit_website_btn.clicked.connect(self.visit_website)
        visit_website_btn.setMinimumWidth(150)
        
        support_layout.addWidget(support_text)
        support_layout.addWidget(visit_website_btn, alignment=Qt.AlignCenter)
        support_group.setLayout(support_layout)
        
        # 许可证信息部分
        license_group = QGroupBox("许可证信息")
        license_layout = QVBoxLayout()
        
        license_text = QTextBrowser()
        license_text.setPlainText("""
FullCycleFileShield (FCFS) 软件许可协议

1. 版权声明
版权所有 © 2026 陈修祺(ChenXiuQi)（个人）。保留所有权利。

2. 许可授予
作者特此授予用户个人非商业性使用软件的不可转让、非独占许可，条件是用户遵守本协议的所有条款和条件。

3. 授权范围
用户有权：
- 在个人设备上安装和使用软件
- 出于个人学习、研究和非商业目的使用软件
- 制作软件的备份副本用于个人存档目的

4. 使用限制
用户不得：
- 将软件用于任何商业目的，包括但不限于商业运营、商业服务或产生商业收益
- 在任何商业环境中部署或使用软件
- 对软件进行任何形式的修改、改编、翻译或二次开发
- 以任何形式分发、传播、共享或转让软件给第三方
- 以任何形式倒卖、转售软件或其衍生作品
- 删除、修改或隐藏软件中的版权声明和许可信息
- 将软件用于任何违法或侵权行为

5. 知识产权
软件的所有知识产权，包括但不限于版权、商标、专利、商业秘密和其他相关权利，均归作者所有。

6. 免责声明
软件按"原样"提供，作者不提供任何形式的保证。在法律允许的最大范围内，作者不对因使用或无法使用软件而导致的任何损害承担责任。

7. 许可终止
在以下情况下，本许可将自动终止：
- 用户违反本协议的任何条款或条件
- 用户以任何方式侵犯软件的知识产权
- 用户将软件用于任何商业目的

8. 法律适用
本协议受中华人民共和国法律管辖。因本协议产生的或与本协议有关的任何争议，应提交至软件作者所在地有管辖权的人民法院诉讼解决。

9. 生效日期
本许可协议自用户首次使用软件之日起生效，版本：1.0.3，发布日期：2026-02-03
        """)
        license_text.setReadOnly(True)
        license_layout.addWidget(license_text)
        license_group.setLayout(license_layout)
        
        # 添加所有组件到主布局
        main_layout.addWidget(info_group)
        main_layout.addWidget(description_group)
        main_layout.addWidget(support_group)
        main_layout.addWidget(license_group)
        
        # 设置主布局
        self.setLayout(main_layout)
    
    def visit_website(self):
        """
        访问官网
        """
        QDesktopServices.openUrl(QUrl("http://fcfs.free.nf"))
