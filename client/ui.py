# _*_ coding: utf-8 _*_import re
import re
import platform
from os import (walk, sep, system)
from os.path import (join, splitext, exists)

from PyQt5.QtGui import QKeyEvent
from PyQt5.QtWidgets import (
    QApplication, QMessageBox, QFileDialog, QWidget,
    QLabel, QLineEdit, QTextEdit, QRadioButton, QToolButton, QPushButton, QTextBrowser,
	QButtonGroup, QFrame, QListWidget, QListWidgetItem, QTabWidget,
    QHBoxLayout, QVBoxLayout, QGridLayout)

from PyQt5.QtCore import (Qt, QTimer, QTranslator)
from threading import Thread
from Queue import Queue
from time import sleep
from datetime import datetime


class MainWindow(QWidget):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
#        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
#        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(500, 300)

        # self.__pbn_switch_view = None

        # 创建窗口部件
        self.widget_frame = QLabel()

        # 窗口标题
        self.title_fram = QLabel()
        self.title = QLabel('MINET')
        self.title.setAlignment(Qt.AlignCenter)
        self.title_fram.setFixedHeight(100)

        # 登录部分

        self.login_btn_fram = QLabel()
        self.login_input_fram = QLabel()
        self.username_lab = QLabel("用户名：")
        self.password_lab = QLabel("密码：")
        self.username_edit = QLineEdit()
        self.password_edit = QLineEdit()
        self.login_btn = QPushButton('登录')
        self.register_btn = QPushButton('注册')
        self.login_btn.setFixedWidth(100)
        self.register_btn.setFixedWidth(100)

        # 显示详细聊天部分
        self.tabView = QTabWidget()
        self.group_chat = QTextBrowser()
        self.P2P_chat = QTextBrowser()
        self.tabView.addTab(self.group_chat, '群聊')
        self.tabView.addTab(self.P2P_chat, 'P2P聊天')

        self.chat_msg_edit = QTextEdit()
        self.send_msg_btn = QPushButton('发送')
        self.chat_msg_edit.setMaximumHeight(80)
        self.chat_msg_edit.setPlaceholderText("有什么想说的？")


        # 布局
        # 标题部分
        self.__layout_title = QHBoxLayout()
        self.__layout_title.addWidget(self.title)
        self.title_fram.setLayout(self.__layout_title)

        # 登录部分
        self.login_input_layout = QGridLayout()
        self.login_input_layout.addWidget(self.username_lab, 0, 0, 1, 1)
        self.login_input_layout.addWidget(self.password_lab, 1, 0, 1, 1)
        self.login_input_layout.addWidget(self.username_edit, 0, 1, 1, 3);
        self.login_input_layout.addWidget(self.password_edit, 1, 1, 1, 3);
        self.login_input_layout.setContentsMargins(0, 0, 0, 0)

        self.login_btn_layout = QHBoxLayout()
        self.login_btn_layout.addWidget(self.login_btn)
        self.login_btn_layout.addWidget(self.register_btn)
        self.login_btn_layout.setContentsMargins(0, 0, 0, 0)

        self.login_input_fram.setFixedHeight(100)
        self.login_input_fram.setLayout(self.login_input_layout)
        self.login_btn_fram.setLayout(self.login_btn_layout)


        # 登录部分widget
        self.login_layout = QVBoxLayout()
        self.login_layout.addWidget(self.login_input_fram)
        self.login_layout.addWidget(self.login_btn_fram)

        self.login_widget = QLabel()
        self.login_widget.setLayout(self.login_layout)

        # 聊天部分widget
        self.chat_layout = QVBoxLayout()
        self.chat_layout.addWidget(self.tabView)
        self.chat_layout.addWidget(self.chat_msg_edit)
        self.chat_layout.addWidget(self.send_msg_btn)

        self.chat_widget = QLabel()
        self.chat_widget.setLayout(self.chat_layout)

        # 顶部层
        self.top_layout = QVBoxLayout()
        self.top_layout.addWidget(self.title_fram)
        self.top_layout.addWidget(self.login_widget)
        self.top_layout.addWidget(self.chat_widget)
        self.top_layout.setSpacing(10)

        self.widget_frame.setLayout(self.top_layout)

        self.layout_fram = QGridLayout()
        self.layout_fram.addWidget(self.widget_frame, 0, 0, 1, 1)
        self.layout_fram.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout_fram)

        # set object name
        self.widget_frame.setObjectName('frame')
        self.title.setObjectName('title')
        self.tabView.setObjectName('tabView')
        self.group_chat.setObjectName('group_chat')
        self.P2P_chat.setObjectName('P2P_chat')
        self.chat_msg_edit.setObjectName('chat_msg_edit')

        self.setStyleSheet(
            '#frame{'
                'border-image: url(Images/bg);'
            '}'
            '#title{'
                'color: white;'
                'font-size: 20pt;'
            '}'
            '#open_tool{'
                'color: black;'
            '}'
            '#mode_fram{'
                # 'border-top: 1px solid rgba(20, 20, 20, 100);'
                # 'border-bottom: 1px solid rgba(20, 20, 20, 100);'
                'background: rgba(200, 200, 200, 40);'
            '}'
            '#ln_open_tool, #ln_path{'
                'border-top-left-radius:    2px;'
                'border-bottom-left-radius: 2px;'
            '}'
            '#ln_pattern{'
                'border-radius: 2px;'
            '}'
            '#state{'
                'background: rgba(200, 200, 200, 40);'
                'border-radius: 2px;'
                'padding: 1px;'
                'color: rgb(240, 240, 240);'
            '}'
            'QTabBar::tab {'
                'border: 0;'
                'width:  100px;'
                'height: 20px;'
                'margin: 0 2px 0 0;'        # top right bottom left
                # 'border-top-left-radius: 5px;'
                # 'border-top-right-radius: 5px;'
                'color: rgb(200, 255, 255;);'
            '}'
            'QTabBar::tab:selected{'
                'background: rgba(25, 255, 255, 40);'
                'border-left: 1px solid rgba(255, 255, 255, 200);'
                'border-top: 1px solid rgba(255, 255, 255, 200);'
                'border-right: 1px solid rgba(255, 255, 255, 200);'
            '}'
            'QTabWidget:pane {'
                'border: 1px solid rgba(255, 255, 255, 200);'
                'background: rgba(0, 0, 0, 80);'
            '}'
            '#group_chat, #P2P_chat{'
                'background: rgba(0, 0, 0, 0);'
                'color: white;'
                'border: 0;'
            '}'
            '#chat_msg_edit{'
                'background: rgba(0, 0, 0, 40);'
                'border: 1px solid rgba(220, 220, 220, 200);'
                'color: white;'
                'height: 10px;'
            '}'
            'QLineEdit{'
                'background: rgba(0, 0, 0, 40);'
                'border: 1px solid rgba(220, 220, 220, 200);'
                'color: white;'
                'height: 20px;'
            '}'
            'QPushButton{'
                'background: rgba(0, 0, 0, 100);'
                'border-radius: 15px;'
                'height: 25px;'
                'color: white;'
            '}'
            'QPushButton::hover{'
                'background: rgba(0, 0, 0, 150);'
            '}'
            'QToolButton{'
                'background: rgba(100, 100, 100, 100);'
                'color: white;'
                'border-top-right-radius:    2px;'
                'border-bottom-right-radius: 2px;'
            '}'
            'QToolButton::hover{'
                'background: rgba(0, 0, 0, 150);'
            '}'
            )


        self.login_btn.setShortcut(Qt.Key_Return)

        # 关联 信号/槽
        self.login_btn.clicked.connect(self.login)
        self.register_btn.clicked.connect(self.register)
        self.send_msg_btn.clicked.connect(self.send_msg)
        self.chat_msg_edit.textChanged.connect(self.detect_return)

        # 线程间共享数据队列
        queue_size = 10000
        self.__queue_result = Queue(queue_size)
        self.__queue_error = Queue(queue_size)

        # 强制结束子线程
        self.__thread_killer = False

        self.chat_widget.hide()
        # self.chat_layout_widgets = [self.tabView, self.chat_msg_edit, self.send_msg_btn]
        # self.login_layout_widgets = [self.login_btn_fram, self.login_input_fram]

    # 检测回车，检测到就发送
    def detect_return(self):
        content = self.chat_msg_edit.toPlainText()
        print "%r" % content
        if content.endswith('\n'):
            self.send_msg_btn.click()


    def login(self):
        print "username:"+self.username_edit.text()
        print "password:"+self.password_edit.text()
        QMessageBox.information(
            self,
            "提示",
            "登录成功！",
            QMessageBox.Yes)
        if self.chat_widget.isHidden():
            self.login_widget.hide()
            self.chat_widget.show()
            self.resize(1000, 800)
        else:
            self.chat_widget.hide()
            self.resize(500, 300)


    def register(self):
        QMessageBox.information(
            self,
            "提示",
            "注册完成！",
            QMessageBox.Yes)


    def send_msg(self):

        currentWidgetName = self.tabView.currentWidget().objectName()
        content = self.chat_msg_edit.toPlainText()
        time = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        self.chat_msg_edit.clear()
        if currentWidgetName == 'group_chat':
            self.group_chat.setText("%s%s\n%s\n"%(self.group_chat.toPlainText(), time, content))
            self.group_chat.moveCursor(self.group_chat.textCursor().End)
        else:
            self.P2P_chat.setText("%s%s\n%s\n"%(self.P2P_chat.toPlainText(), time, content))
            self.P2P_chat.moveCursor(self.P2P_chat.textCursor().End)



# 程序入口
if __name__ == '__main__':
    import sys
    translator = QTranslator()
    translator.load('/home/bill/Qt5.5.1/5.5/gcc_64/translations/qt_zh_CN.qm')
    app = QApplication(sys.argv)
    app.installTranslator(translator)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
