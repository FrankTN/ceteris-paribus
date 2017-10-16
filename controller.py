import sys
from PyQt5.QtWidgets import QFileDialog, QApplication
from tinydb import TinyDB

from gui.GUI import modelWindow
from model import Model

class Controller(object):

    def __init__(self):
        self.gui = modelWindow(self)

    def get_db(self):
        return self.db

    def set_db(self, dbpath: str):
        try:
            self.db = TinyDB(dbpath)
            self.model = Model(self)
            return 1
        except Exception:
            return 0

    def get_organ(self, index):
        return self.model.get_organ(index)

    def get_organ_names(self):
        names = list(map(lambda x: x.get_name(), self.model.get_systemic().vertices()))
        return names

    def set_total_VO2(self):
        self.gui.setGlobalVO2(self.model.calculate_total_VO2())

    def global_slider_changed(self, changeSender):
        self.model.globalChanged(changeSender)
        self.set_total_VO2()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    controller = Controller()
    sys.exit(app.exec_())
