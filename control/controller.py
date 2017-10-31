""" The controller acts as a layer handling communication between the GUI, the model and the database. """
#TODO this will be refactored into multiple smaller parts
import sys

from PyQt5.QtWidgets import QApplication

from gui.dialogs import select_db_dialog
from gui.graph_editor import graphWindow
from model.globalmodel import GlobalModel


class Controller(object):

    def __init__(self):
        # First we ask the user to select a database
        self.db = select_db_dialog()
        # Next, we create a model based on the database
        self.model = GlobalModel(self)
        # Finally, a UI is instantiated based on the current model
        self.ui = graphWindow(self)

    def open_new_db(self):
        self.db = select_db_dialog()
        self.model = GlobalModel(self)
        # After changing the model and the database inside the controller, we ask the UI to update itself
        self.ui.update_model(self)

    def get_model(self):
        return self.model

    def get_db(self):
        return self.db

    def get_global_params(self):
        # This function provides a layer of abstraction so other object do not need to know about the existence of the
        # model
        return self.model.get_global_params()

    def param_changed(self, name: str, slider):
        # Another relay method to ensure the model is only used by the controller
        self.model.param_changed(name, slider)

if __name__ == "__main__":
    # The starting point for the entire program, creates a QApplication and runs the controller.
    app = QApplication(sys.argv)
    controller = Controller()
    sys.exit(app.exec_())
