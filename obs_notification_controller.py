import sys
from ui_notification import Ui_Notification
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import (QCoreApplication, QPropertyAnimation, QDate, QDateTime, QMetaObject, QObject, QPoint, QRect, QSize, QTime, QUrl, Qt, QEvent)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor, QFont, QFontDatabase, QIcon, QKeySequence, QLinearGradient, QPalette, QPainter, QPixmap, QRadialGradient)
from PySide6.QtWidgets import *

counter = 0

class Notification(QMainWindow):
    def __init__(self, message):
        QMainWindow.__init__(self)
        self.ui = Ui_Notification()
        self.ui.setupUi(self)

        # Remove Borders and Background
        # Always on top
        self.move(0, 0)
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        #self.setFocus(False)

        self.ui.msg.setText(message)
        self.ui.msg.adjustSize()

        MARGIN_LEFT = 3
        MARGIN_RIGHT = 35
        MARGIN = MARGIN_LEFT + MARGIN_RIGHT
        BUFFER = 10

        new_width = self.ui.msg.width() + MARGIN
        self.resize(new_width, self.height())

        self.ui.progressBar.resize(new_width + BUFFER, self.ui.progressBar.height())

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.progress)
        # TIMER IN MILLISECONDS
        self.timer.start(16)

        self.show()

    def progress(self):
        global counter
        self.ui.progressBar.setValue(counter)
        counter += 1
        if counter > 100:
            counter = 0
            self.timer.stop()
            self.close()

def create_notification(message: str) -> None:
    if not QtWidgets.QApplication.instance():
        app = QtWidgets.QApplication(sys.argv)
    else:
        app = QtWidgets.QApplication.instance()
    window = Notification(message)
    sys.exit(app.exec_())

if __name__ == "__main__":
    if len(sys.argv) > 1:
        create_notification(sys.argv[1])