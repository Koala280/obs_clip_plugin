# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'notificationFnKJta.ui'
##
## Created by: Qt User Interface Compiler version 6.1.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *


class Ui_Notification(object):
    def setupUi(self, Notification):
        if not Notification.objectName():
            Notification.setObjectName(u"Notification")
        Notification.resize(130, 45)
        self.centralwidget = QWidget(Notification)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setSpacing(10)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(1, 1, 1, 1)
        self.background = QFrame(self.centralwidget)
        self.background.setObjectName(u"background")
        self.background.setStyleSheet(u"QFrame {\n"
"	background-color: rgb(54, 58, 89);\n"
"	color: rgb(218, 218, 218);\n"
"	border-radius:9px;\n"
"}")
        self.background.setFrameShape(QFrame.StyledPanel)
        self.background.setFrameShadow(QFrame.Raised)
        self.msg = QLabel(self.background)
        self.msg.setObjectName(u"msg")
        self.msg.setGeometry(QRect(10, 3, 91, 31))
        font = QFont()
        font.setPointSize(17)
        font.setBold(False)
        font.setItalic(False)
        font.setUnderline(False)
        self.msg.setFont(font)
        self.msg.setStyleSheet(u"color: rgb(254, 121, 199);")
        self.msg.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)
        self.progressBar = QProgressBar(self.background)
        self.progressBar.setObjectName(u"progressBar")
        self.progressBar.setGeometry(QRect(1, 34, 128, 2))
        self.progressBar.setMinimumSize(QSize(0, 2))
        self.progressBar.setMaximumSize(QSize(16777215, 2))
        self.progressBar.setStyleSheet(u"QProgressBar {\n"
"	background-color: rgb(54, 58, 89);\n"
"	color: rgba(255, 255, 255, 0);\n"
"	border-style: none;\n"
"}\n"
"\n"
"QProgressBar::chunk {\n"
"	border-radius: 10px;\n"
"	background-color: qlineargradient(spread:pad, x1:0, y1:0.511364, x2:1, y2:0.523, stop:0 rgba(254, 121, 199, 255), stop:1 rgba(170, 85, 255, 255));\n"
"}")
        self.progressBar.setMaximum(100)
        self.progressBar.setValue(100)
        self.progressBar.setTextVisible(True)

        self.verticalLayout.addWidget(self.background)

        Notification.setCentralWidget(self.centralwidget)

        self.retranslateUi(Notification)

        QMetaObject.connectSlotsByName(Notification)
    # setupUi

    def retranslateUi(self, Notification):
        Notification.setWindowTitle(QCoreApplication.translate("Notification", u"MainWindow", None))
        self.msg.setText(QCoreApplication.translate("Notification", u"Message", None))
        self.progressBar.setFormat(QCoreApplication.translate("Notification", u"%p%", None))
    # retranslateUi

