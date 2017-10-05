import sys
from PyQt5 import QtGui, uic
from PyQt5.QtWidgets import QMainWindow, QApplication


class MyWindow(QMainWindow):
    def __init__(self):
        super(MyWindow, self).__init__()
        uic.loadUi('First.ui', self)
        self.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyWindow()
    sys.exit(app.exec_())