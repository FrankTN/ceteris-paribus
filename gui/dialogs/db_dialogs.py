""" This module contains code for the generic"""

from PyQt5.QtWidgets import QFileDialog, QMessageBox
from tinydb import TinyDB

def select_db_dialog():
    """ This function, which opens the database and connects it to the model is called before the UI can actually be
        used. """
    qfd = QFileDialog()
    qfd.setNameFilter("*.json")
    # A lambda is needed here so exit() is not called directly
    qfd.rejected.connect(lambda: exit())
    qfd.exec_()
    # We can only select a single file, therefore, we can always look at [0] without missing anything
    potential_db = qfd.selectedFiles()[0]
    try:
        return TinyDB(potential_db)
    except:
        # If we were unable to open the database for whatever reason we give the user another chance.
        msg = QMessageBox()
        msg.setText("Unable to load database, the file might be corrupted\nPlease try again")
        msg.exec_()
        select_db_dialog()

def save_db_dialog():
    """ This function creates a graphical interface to save a file. It returns the name of the target"""
    return QFileDialog.getSaveFileName(None, "Save File", "/home","*.json")[0]

def remove_selected(var_view, variables):
    # Removes the selected item from the specified widget and from the corresponding item:value dict
    for selected in var_view.selectedItems():
        var_view.takeItem(var_view.row(selected))
        var_name = selected.text().split("=>")[0].strip()
        variables.pop(var_name)
