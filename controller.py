""" The controller acts as a layer handling communication between the GUI and the model. """
import sys
from PyQt5.QtWidgets import QFileDialog, QApplication
from tinydb import TinyDB

from gui.GUI import modelWindow
from model import Model

class Controller(object):

    def __init__(self):
        self.gui = modelWindow(self)

    def get_db(self):
        try:
            return self.db
        except AttributeError:
            print("Database not found!")
            self.gui.open_db()

    def set_db(self, dbpath: str):
        try:
            self.db = TinyDB(dbpath)
            self.model = Model(self)
            return True
        except Exception:
            print("An exception occurred when opening the database")
            return False

    def get_organ(self, index):
        return self.model.get_organ(index)

    def get_organ_names(self):
        names = list(map(lambda x: x.get_name(), self.model.get_systemic().vertices()))
        return names

    def global_slider_changed(self, changeSender):
        self.model.update_model(changeSender.objectName(), changeSender.value())
        self.gui.set_global_VO2(self.model.calculate_total_VO2())
        self.gui.set_global_VCO2(self.model.calculate_total_VCO2())
        self.gui.set_global_RQ(self.model.calculate_total_RQ())
        self.gui.set_spec_VO2(self.model.calculate_spec_VO2())
        self.gui.set_spec_VCO2(self.model.calculate_spec_VCO2())
        # set dependent organ variables
        self.gui.select_organ(self.gui.organ_index)
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    controller = Controller()
    sys.exit(app.exec_())
