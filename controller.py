import sys
from PyQt5.QtWidgets import QFileDialog, QApplication
from tinydb import TinyDB

from gui.GUI import modelWindow
from model import Model

class Controller(object):

    def __init__(self):
        self.gui = modelWindow(self)

    def getdb(self):
        return self.db

    def setdb(self, dbpath: str):
        try:
            self.db = TinyDB(dbpath)
            self.model = Model(self)
            return 1
        except Exception:
            return 0


    def globalSliderChanged(self, changeSender):
        self.model.globalChanged(changeSender)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    controller = Controller()
    sys.exit(app.exec_())
