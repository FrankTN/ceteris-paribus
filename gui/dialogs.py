""" This module contains code to create all dialogs used by the program"""
from functools import partial

from PyQt5.QtCore import Qt, QStringListModel
from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtWidgets import QDialog, QHBoxLayout, QPushButton, QGridLayout, QLabel, QLineEdit, QFileDialog, QSlider, \
    QVBoxLayout, QMessageBox, QListWidget, QListWidgetItem, QCompleter, QGroupBox
from tinydb import TinyDB

from gui.validator import FunctionValidator


class NewNodeDialog(QDialog):
    """ This class is used when creating new nodes"""
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.organ_variables = {}

        self.name_next_button = QPushButton("&Next")
        self.name_next_button.setEnabled(False)
        cancelButton = QPushButton("Cancel")

        self.name_next_button.clicked.connect(self.set_source)
        cancelButton.clicked.connect(self.reject)
        self.setWindowTitle("Create new node")

        name_layout = QHBoxLayout()
        nameLabel = QLabel("&Name:")
        self.nameField = QLineEdit()
        self.nameField.textChanged.connect(self.validate_text_field)

        nameLabel.setBuddy(self.nameField)
        name_layout.addWidget(nameLabel)
        name_layout.addWidget(self.nameField)

        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch()
        buttonLayout.addWidget(self.name_next_button)
        buttonLayout.addWidget(cancelButton)

        layout = QGridLayout()
        layout.addLayout(name_layout, 0, 0)
        layout.addLayout(buttonLayout, 2, 0, 1, 3)
        self.setLayout(layout)

    def validate_text_field(self):
        if not self.isEmpty(self.nameField.text()):
            self.name = self.nameField.text()
            self.name_next_button.setEnabled(True)
        else:
            self.name_next_button.setEnabled(False)

    def isEmpty(self, string: str):
        return string.strip() is ""

    def set_source(self):
        # This dialog requires the user to enter a source
        self.src_dialog = QDialog()
        self.src_dialog.setWindowTitle("Select sources")
        layout = QGridLayout()
        self.list_view = QListWidget()
        self.list_view.itemSelectionChanged.connect(self.validate_list)

        # We manually add an item for the global inputs
        input_widget = QListWidgetItem()
        input_widget.setText("Global Input")
        self.list_view.addItem(input_widget)

        for item in list(self.controller.get_model().get_organs().keys()):
            if item is not '__builtins__':
                widget = QListWidgetItem()
                widget.setText(item)
                self.list_view.addItem(widget)

        self.name_next_button = QPushButton("&Next")
        self.name_next_button.setEnabled(False)
        back_button = QPushButton("Back")

        self.name_next_button.clicked.connect(self.define_variables)
        back_button.clicked.connect(self.src_dialog.reject)

        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch()
        buttonLayout.addWidget(self.name_next_button)
        buttonLayout.addWidget(back_button)

        layout.addWidget(self.list_view)
        layout.addLayout(buttonLayout, 1, 0)
        self.src_dialog.setLayout(layout)
        self.src_dialog.exec_()

    def validate_list(self):
        # This function enables the next button once items have been selected
        if self.list_view.selectedItems():
            self.src_edge_item = self.list_view.selectedItems()
            self.name_next_button.setEnabled(True)
        else:
            self.name_next_button.setEnabled(False)

    def define_variables(self):
        # This dialog is used to define the variables which are used by the organs
        self.var_dialog = QDialog()
        self.var_dialog.setWindowTitle("Define variables")
        layout = QGridLayout()

        self.var_view = QListWidget()

        edit_group = QGroupBox()
        edits = QGridLayout()
        edits.addWidget(QLabel("Variable name"), 0, 0)
        self.var_name = QLineEdit()
        edits.addWidget(self.var_name, 0, 1)

        self.var_min = QLineEdit()
        self.var_min.setValidator(QDoubleValidator())
        edits.addWidget(QLabel("Min"), 1, 0)
        edits.addWidget(self.var_min, 1, 1)
        self.var_max = QLineEdit()
        self.var_max.setValidator(QDoubleValidator())
        edits.addWidget(QLabel("Max"), 2, 0)
        edits.addWidget(self.var_max, 2, 1)
        self.var_val = QLineEdit()
        self.var_val.setValidator(QDoubleValidator())
        edits.addWidget(QLabel("Val"), 3, 0)
        edits.addWidget(self.var_val, 3, 1)

        add_button = QPushButton("Add Variable")
        add_button.clicked.connect(self.add_var)
        del_button = QPushButton("Remove selected")
        del_button.clicked.connect(partial(self.remove_selected, self.var_view, self.organ_variables))
        edits.addWidget(add_button)
        edits.addWidget(del_button)
        edit_group.setLayout(edits)

        buttons = QHBoxLayout()
        next_button = QPushButton("Next")
        back_button = QPushButton("Back")

        next_button.clicked.connect(self.define_functions)
        back_button.clicked.connect(self.var_dialog.reject)

        buttons.addStretch()
        buttons.addWidget(next_button)
        buttons.addWidget(back_button)

        layout.addWidget(self.var_view, 0, 0)
        layout.addWidget(edit_group, 1, 0)
        layout.addLayout(buttons, 2, 0)

        self.var_dialog.setLayout(layout)
        self.var_dialog.exec_()

    def add_var(self):
        # The function which is called when the "Add Variable" button is clicked
        minimum = float(self.var_min.text())
        maximum = float(self.var_max.text())
        value = float(self.var_val.text())

        # A name is valid if it is not empty after stripping all the whitespace
        valid_name = not self.var_name.text().strip() == ""
        # If we have a valid name and the value is between the minimum and the maximum, we add the item
        if valid_name and minimum <= value <= maximum:
            self.var_view.addItem(QListWidgetItem(self.var_name.text() + " => [min: " + str(minimum) + ", max: " +
                                                  str(maximum) + ", val: " + str(value) + "]"))
            self.organ_variables[self.var_name.text()] = [minimum, maximum, value]
            self.var_name.clear()
            self.var_min.clear()
            self.var_max.clear()
            self.var_val.clear()

    def remove_selected(self, list_widget, value_dict):
        # Removes the selected item from the specified widget and from the corresponding item:value dict
        for selected in list_widget.selectedItems():
            list_widget.takeItem(list_widget.row(selected))
            var_name = selected.text().split("=>")[0].strip()
            value_dict.pop(var_name)

    def define_functions(self):
        # This shows a dialog for defining the functions used by the organ. These functions can use the variables which
        # have just been defined
        selected_strings = self.list_view.selectedItems()
        self.sources = []
        organ_vars = []

        for organ_name_widget in selected_strings:
            # We handle the global input source differently, as it requires the global parameters
            if organ_name_widget.text() == "Global Input":
                organ_vars.append(self.controller.get_global_param_ranges())
            else:
                self.sources.append(self.controller.get_model().get_organs()[organ_name_widget.text()])
        # organ_vars is a list of dicts containing the ranges of all variables keyed by the variable name
        organ_vars += [x.local_ranges() for x in self.sources]

        # flattened vars is the dict containing all the variables taken together
        self.flattened_vars = {}
        for var_dict in organ_vars:
            self.flattened_vars = {**var_dict, **self.flattened_vars}

        # For some inexplicable reason, the builtins keep appearing in the variables, they need to be popped
        self.flattened_vars.pop('__builtins__', None)
        self.flattened_vars = {**self.flattened_vars, **self.organ_variables}
        # Concatenate the lists of keys, thus obtaining the variable names as strings
        organ_var_strings = self.flattened_vars.keys()

        # Create an autocompleter to autocomplete the variable names
        autocomplete_model = QStringListModel()
        autocomplete_model.setStringList(organ_var_strings)
        autocompleter = QCompleter()
        autocompleter.setModel(autocomplete_model)

        # Create the actual dialog which can be used to create the functions
        self.fnc_dialog = QDialog()
        self.name_next_button = QPushButton("Finish")
        self.name_next_button.clicked.connect(self.finalize)
        back_button = QPushButton("Back")
        back_button.clicked.connect(self.fnc_dialog.reject)

        # Add the next and back buttons
        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch()
        buttonLayout.addWidget(self.name_next_button)
        buttonLayout.addWidget(back_button)

        self.functions = {}

        flexible_grid = QHBoxLayout()
        self.function_list_widget = QListWidget()
        flexible_grid.addWidget(self.function_list_widget)

        # Create the edit fields to hold the variable names and functions
        edits = QHBoxLayout()
        self.f_name = QLineEdit()
        self.f_form = QLineEdit()
        self.f_form.setCompleter(autocompleter)
        edits.addWidget(self.f_name)
        edits.addWidget(self.f_form)
        self.f_form.setValidator(FunctionValidator(self.flattened_vars))

        # Add buttons for adding and removing functions and connect them
        add_button = QPushButton("Add Function")
        add_button.clicked.connect(self.addFunction)
        remove_button = QPushButton("Remove Selected")
        remove_button.clicked.connect(partial(self.remove_selected, self.function_list_widget, self.functions))
        edits.addWidget(add_button)
        edits.addWidget(remove_button)

        # Create the layout for the entire dialog
        layout = QGridLayout()
        layout.addLayout(flexible_grid, 0, 0)
        layout.addLayout(edits, 1, 0)
        layout.addLayout(buttonLayout, 2, 0)

        self.fnc_dialog.setLayout(layout)
        self.fnc_dialog.exec_()

    def addFunction(self):
        # A function is valid if it is returned as such by the validator
        self.f_form.validator().setConfirmed(True)
        valid_function = self.f_form.hasAcceptableInput()
        # A name is valid as long as its not empty
        valid_name = not self.f_name.text().strip() == ""
        if valid_name and valid_function:
            self.functions[self.f_name.text()] = self.f_form.text()
            self.function_list_widget.addItem(QListWidgetItem(self.f_name.text() + " => " + self.f_form.text()))
            self.f_form.validator().setConfirmed(False)
            self.f_form.clear()

    def finalize(self):
        # Closes all remaining dialogs, this is called when the finish button is clicked
        self.fnc_dialog.accept()
        self.src_dialog.accept()
        self.var_dialog.accept()
        self.accept()

    def get_edge_item(self):
        return self.src_edge_item

    def get_name(self):
        return self.name

    def get_variables(self):
        # Return the variables after making sure that the builtins module is not included
        self.flattened_vars.pop('__builtins__', None)
        return self.flattened_vars

    def get_funcs(self):
        return self.functions

def select_db_dialog():
    """ This function, which opens the database and connects it to the model is called before the UI can actually be
        used. """
    qfd = QFileDialog()
    qfd.setNameFilter("*.json")
    # A lambda is needed here so exit() is not called directly
    qfd.rejected.connect(lambda : exit())
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
