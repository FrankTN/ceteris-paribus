#!/usr/bin/env python3

""" The controller acts as a layer handling communication between the GUI, the model and the database. """
import os.path
import sys

# Append the parent directory of this file to the global path. This ensures that we may always find the required modules
# irrespective of the starting directory.
from ceteris_paribus.control.model_control import ModelController
from ceteris_paribus.control.view_control import ViewController

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from PyQt5.QtWidgets import QApplication

from ceteris_paribus.gui.dialogs.db_dialogs import select_db_dialog


class Controller(object):
    """ The controller contains the main function. It oversees program execution and provides an interface between the
        model and the User Interface."""

    def __init__(self):
        # Create a view control object and a model control object, to be used by this controller
        self.view_control = ViewController(self)

    def open_new_db(self):
        # Change to a new database, opens a UI dialogs
        self.db = select_db_dialog()
        self.model_control = ModelController(self.db)

    def get_model_control(self):
        return self.model_control

    def get_model(self):
        return self.model_control.model

    def get_outputs(self):
        return

    def get_global_param_ranges(self):
        return self.model_control.get_global_param_ranges()

if __name__ == "__main__":
    # The starting point for the entire program, creates a QApplication object.
    app = QApplication(sys.argv)
    controller = Controller()
    sys.exit(app.exec_())
