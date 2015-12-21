# _*_ coding: utf-8 _*_import re
import re
import platform
from os import (walk, sep, system)
from os.path import (join, splitext, exists)
from PyQt5.QtWidgets import (QApplication, QMessageBox, QFileDialog, QWidget,
                             QLabel, QLineEdit, QRadioButton, QToolButton, QPushButton, QTextBrowser,
			     QButtonGroup, QFrame, QListWidget, QListWidgetItem, QListWidget, QListWidgetItem, QTabWidget,
                             QHBoxLayout, QVBoxLayout, QGridLayout)

from PyQt5.QtCore import (Qt, QTimer)
from threading import Thread
from Queue import Queue
from time import sleep


class MainWindow(QWidget):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
#        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
#        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(900, 300)

        # self.__pbn_switch_view = None

        # 创建窗口部件
        self.widget_frame = QLabel()

        # window title
        self.title_fram = QLabel()
        self.title = QLabel('MI')
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
        # for w in [self.username_lab, self.password_lab, self.username_edit, self.password_edit]:
        #     w.setFixedWidth(35)
        #     w.setContentsMargins(60, 0, 60, 0)
            #w.setFixedHeight(100)

        # 显示详细部分
        self.tabView = QTabWidget()
        self.group_chat = QListWidget()
        self.P2P_chat = QTextBrowser()
        self.tabView.addTab(self.group_chat, '群聊')
        self.tabView.addTab(self.P2P_chat, 'P2P聊天')

        # lines
        '''
        self.__line_1 = QFrame()
        self.__line_1.setFrameStyle(QFrame.HLine | QFrame.Sunken)
        '''
        # 布局
        # window title
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

        # top layout
        self.top_layout = QVBoxLayout()
        self.top_layout.addWidget(self.title_fram)
        self.top_layout.addWidget(self.login_input_fram)
        self.top_layout.addWidget(self.login_btn_fram)
        self.top_layout.addWidget(self.tabView)
        self.top_layout.setSpacing(10)
        self.widget_frame.setLayout(self.top_layout)

        self.layout_fram = QGridLayout()
        self.layout_fram.addWidget(self.widget_frame, 0, 0, 1, 1)
        self.layout_fram.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout_fram)

        # set object name
        self.widget_frame.setObjectName('fram')
        self.title.setObjectName('lab_title')
        self.tabView.setObjectName('tabView')
        self.group_chat.setObjectName('browser_result')
        self.P2P_chat.setObjectName('browser_error')

        self.setStyleSheet(
            '#fram{'
                'border-image: url(Images/bg);'
            '}'
            '#lab_title{'
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
            '#browser_result, #browser_error{'
                'background: rgba(0, 0, 0, 0);'
                'border: 0;'
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
        # self.__pbn_file_path.clicked.connect(self.choose_path)
        self.login_btn.clicked.connect(self.login)
        self.register_btn.clicked.connect(self.register)

        # 线程间共享数据队列
        queue_size = 10000
        self.__queue_result = Queue(queue_size)
        self.__queue_error = Queue(queue_size)

        # 强制结束子线程
        self.__thread_killer = False

        self.tabView.hide()


    def login(self):
        print "username:"+self.username_edit.text()
        print "password:"+self.password_edit.text()
        QMessageBox.information(
            self,
            "提示",
            "登录成功！",
            QMessageBox.Yes)
        if self.tabView.isHidden():
            self.login_input_fram.hide()
            self.login_btn_fram.hide()
            self.tabView.show()
            self.resize(900, 900)
        else:
            self.tabView.hide()
            self.resize(900, 300)


    def register(self):
        QMessageBox.information(
            self,
            "提示",
            "注册完成！",
            QMessageBox.Yes)


# 程序入口
if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    #main_window.set_open_tool()
    sys.exit(app.exec_())
