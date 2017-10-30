""" The controller acts as a layer handling communication between the GUI and the model. """
import sys
from PyQt5.QtWidgets import QFileDialog, QApplication
from tinydb import TinyDB

from gui.dialogs import open_db
from gui.graph_editor import graphWindow
from model import Model

class Controller(object):

    def __init__(self):
        self.db = open_db()
        self.model = Model(self)
        self.ui = graphWindow(self)

    def open_new_db(self):
        self.db = open_db()

    def get_model(self):
        return self.model

    def get_db(self):
        try:
            return self.db
        except AttributeError:
            print("Database not found!")
            self.db = open_db()

    def set_db(self, dbpath: str):
        try:
            self.db = TinyDB(dbpath)
            self.model = Model(self)
            return True
        except Exception:
            print("An exception occurred when opening the database")
            return False

if __name__ == "__main__":
    app = QApplication(sys.argv)
    controller = Controller()
    sys.exit(app.exec_())
