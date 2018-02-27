#!/usr/bin/env python3

""" The controller acts as a layer handling communication between the GUI, the model and the database. """
import os.path
import sys

# Append the parent directory of this file to the global path. This ensures that we may always find the required modules
# irrespective of the starting directory.
from PyQt5.QtGui import QFont

from ceteris_paribus.control.model_control import ModelController
from ceteris_paribus.control.view_control import ViewController
from ceteris_paribus.gui.visual_elements import print_warning

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from PyQt5.QtWidgets import QApplication, QMessageBox

from ceteris_paribus.gui.dialogs.db_dialogs import select_db_dialog


class Controller(object):
    """ The controller contains the main function. It oversees program execution and provides an interface between the
        model and the User Interface."""

    def __init__(self):
        # Create a view control object and a model control object, to be used by this controller
        self.view_control = ViewController(self)
        # Initialize the database and the model controller as empty objects, as we do not have a model to control yet
        self.model_control = None
        self.db = None

    def open_new_db(self):
        # Change to a new database, opens a UI dialog
        self.db = select_db_dialog()
        if self.verify_db(self.db):
            self.model_control = ModelController(self.db)
            return True
        else:
            return False

    def verify_db(self, db):
        try:
            # This function returns True only if the underlying DB has the correct structure
            tables = {'GlobalFunctions', 'GlobalParameters', 'SystemicOrgans', 'GlobalConstants'}
            if len(set(tables).intersection(db.tables())) == 4:
                global_param_table = db.table("GlobalParameters").all()
                for param in global_param_table[0]:
                    if len(global_param_table[0][param]) != 3:
                        print_warning("Unable to read database, global parameters do not define range")
                        return False
                return True
            print_warning("Unable to read database, not all required tables are present")
            return False
        except:
            print_warning("Unspecified error when trying to read the database")
            return False

    def get_model_control(self):
        return self.model_control

    def get_model(self):
        return self.model_control.model

if __name__ == "__main__":
    # The starting point for the entire program, creates a QApplication object.
    app = QApplication(sys.argv)
    new_font = QFont("Arial", 12)
    app.setFont(new_font)
    controller = Controller()
    sys.exit(app.exec_())
