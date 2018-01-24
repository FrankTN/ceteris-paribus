""" This module contains code to create all dialogs used by the program"""
from functools import partial

from PyQt5.QtCore import QStringListModel
from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtWidgets import QDialog, QHBoxLayout, QPushButton, QGridLayout, QLabel, QLineEdit, QFileDialog, QMessageBox, \
    QListWidget, QListWidgetItem, QCompleter, QGroupBox
import pyqtgraph as pg
from gui.validator import FunctionValidator
from tinydb import TinyDB


class NewNodeCreator(object):
    """ This class is used when creating new nodes"""

    def __init__(self, controller):
        super().__init__()
        self.controller = controller

    def run(self):
        name_dialog = NameDialog()
        if name_dialog.exec_():
            # handle name
            self.name = name_dialog.name_field.text()
        else:
            # If we reject during naming return false
            return False
        source_dialog = SourceDialog(self.controller)
        self.variables = {}
        if source_dialog.exec_():
            # handle source
            self.sources = source_dialog.get_source()
            for source in self.sources:
                # Get the source organ, or the global input, according to the name of the source
                if source == "Global Input":
                    self.variables = {**self.variables, **self.controller.get_global_param_ranges()}
                else:
                    locals_of_source = self.controller.get_model().get_organs()[source].get_local_ranges()
                    # Unroll source locals into general variables
                    self.variables = {**self.variables, **locals_of_source}
        else:
            # If we reject during source selection return false
            return False
        var_dialog = VarDialog(self.variables)
        var_dialog.exec_()
        # self.variables has been updated, we can now write functions
        function_dialog = FunctionDialog(self.variables)
        if function_dialog.exec_():
            # handle functions
            self.functions = function_dialog.get_functions()
        else:
            # If we reject during naming return false
            return False
        return True

    def get_variables(self):
        return self.variables

    def get_name(self):
        return self.name

    def get_funcs(self):
        return self.functions

    def get_sources(self):
        return self.sources


class NameDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.next_button = QPushButton("&Next")
        self.next_button.setEnabled(False)
        cancel_button = QPushButton("Cancel")

        self.setWindowTitle("Set new node name")
        name_layout = QHBoxLayout()
        name_label = QLabel("&Name:")
        self.name_field = QLineEdit()
        self.name_field.textChanged.connect(self.validate_text_field)

        name_label.setBuddy(self.name_field)
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_field)

        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch()
        buttonLayout.addWidget(self.next_button)
        buttonLayout.addWidget(cancel_button)

        layout = QGridLayout()
        layout.addLayout(name_layout, 0, 0)
        layout.addLayout(buttonLayout, 2, 0, 1, 3)
        self.setLayout(layout)

        self.next_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)

    def validate_text_field(self):
        if not self.isEmpty(self.name_field.text()):
            self.name = self.name_field.text()
            self.next_button.setEnabled(True)
        else:
            self.next_button.setEnabled(False)

    def isEmpty(self, string):
        return string.strip() is ""


class SourceDialog(QDialog):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller

        self.setWindowTitle("Select sources")
        layout = QGridLayout()
        self.list_view = QListWidget()
        self.list_view.itemSelectionChanged.connect(self.validate_list)

        # We manually add an item for the global inputs
        input_widget = QListWidgetItem()
        input_widget.setText("Global Input")
        self.list_view.addItem(input_widget)

        organ_names = list(self.controller.get_model().get_organs().keys())

        for item in organ_names:
            if item is not '__builtins__':
                widget = QListWidgetItem()
                widget.setText(item)
                self.list_view.addItem(widget)

        self.name_next_button = QPushButton("&Next")
        self.name_next_button.setEnabled(False)
        back_button = QPushButton("Back")

        self.name_next_button.clicked.connect(self.accept)
        back_button.clicked.connect(self.reject)

        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch()
        buttonLayout.addWidget(self.name_next_button)
        buttonLayout.addWidget(back_button)

        layout.addWidget(self.list_view)
        layout.addLayout(buttonLayout, 1, 0)
        self.setLayout(layout)

    def get_source(self):
        # Returns the names of the selected sources
        source_list = []
        for source_widget in self.list_view.selectedItems():
            source_list.append(source_widget.text())
        return source_list

    def validate_list(self):
        # This function enables the next button once items have been selected
        if self.list_view.selectedItems():
            self.name_next_button.setEnabled(True)
        else:
            self.name_next_button.setEnabled(False)

    def get_name(self):
        return self.name

    def get_variables(self):
        # Return the variables after making sure that the builtins module is not included
        self.flattened_vars.pop('__builtins__', None)
        return self.flattened_vars

    def get_funcs(self):
        return self.functions


class VarDialog(QDialog):
    def __init__(self, variables):
        super().__init__()
        self.setWindowTitle("Define variables")
        layout = QGridLayout()

        # First, add all previously defined variables to the list, this is empty if we are working on a new organ
        self.var_list_widget = QListWidget()
        for var in variables:
            list_item = QListWidgetItem()
            var_range = variables[var]
            list_item.setText(var + "\t => [min: " + str(var_range[0]) + ", max: " + str(var_range[1]) + ", val: " +
                              str(var_range[2]) + "]")
            self.var_list_widget.addItem(list_item)
        layout.addWidget(self.var_list_widget)
        self.var_list_widget.itemDoubleClicked.connect(self.update_edits)

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
        add_button.clicked.connect(partial(self.add_var, variables))

        del_button = QPushButton("Remove selected")
        del_button.clicked.connect(partial(remove_selected, self.var_list_widget, variables))
        edits.addWidget(add_button)
        edits.addWidget(del_button)
        edit_group.setLayout(edits)

        buttons = QHBoxLayout()
        next_button = QPushButton("Next")
        back_button = QPushButton("Back")

        # When the next button is clicked, we call the next_function passing it the results
        next_button.clicked.connect(self.accept)
        back_button.clicked.connect(self.reject)

        buttons.addStretch()
        buttons.addWidget(next_button)
        buttons.addWidget(back_button)

        layout.addWidget(self.var_list_widget, 0, 0)
        layout.addWidget(edit_group, 1, 0)
        layout.addLayout(buttons, 2, 0)

        self.setLayout(layout)

    def add_var(self, variables):
        try:
            if self.var_name.text() in variables:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                msg.setText("The name you entered already exists, \nOverwrite?")
                msg.setWindowTitle("Name already exists")
                msg.setStandardButtons(QMessageBox.Yes)
                msg.addButton(QMessageBox.No)
                msg.setDefaultButton(QMessageBox.No)
                if msg.exec() == QMessageBox.No:
                    return
            minimum = float(self.var_min.text())
            maximum = float(self.var_max.text())
            value = float(self.var_val.text())

            # A name is valid if it is not empty after stripping all the whitespace
            valid_name = not self.var_name.text().strip() == ""
            # If we have a valid name and the value is between the minimum and the maximum, we add the item
            if valid_name and minimum <= value <= maximum:
                self.var_list_widget.addItem(QListWidgetItem(self.var_name.text() + "\t => [min: " + str(minimum) + ", max: " +
                                                 str(maximum) + ", val: " + str(value) + "]"))
                variables[self.var_name.text()] = [minimum, maximum, value]
                self.var_name.clear()
                self.var_min.clear()
                self.var_max.clear()
                self.var_val.clear()
            else :
                raise ValueError
        except ValueError:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Incorrect field value was entered, please try again")
            msg.setInformativeText("Please make sure the values are numbers")
            msg.setWindowTitle("Data in field is incorrect")
            if not self.var_min.text():
                min_message = "empty"
            else:
                min_message = self.var_min.text()

            if not self.var_max.text():
                max_message = "empty"
            else:
                max_message = self.var_max.text()

            if not self.var_val.text():
                val_message = "empty"
            else:
                val_message = self.var_val.text()
            msg.setDetailedText("Min: " + min_message + "\n"
                                "Max: " + max_message + "\n"
                                "Val: " + val_message + "\n")
            msg.exec_()

    def update_edits(self):
        for selected in self.var_list_widget.selectedItems():
            self.var_list_widget.item(self.var_list_widget.row(selected))
            var = selected.text().split("=>")
            var_name = var[0].strip()
            var_def_string = var[1].strip()

            # var_def has the form [min: x, max: y, val: z], and we must split the field accordingly
            var_def_list = var_def_string.split()
            # The values are now defined at specified locations, we have:
            var_min = var_def_list[1].rstrip(",")
            self.var_min.setText(var_min)
            var_max = var_def_list[3].rstrip(",")
            self.var_max.setText(var_max)
            var_val = var_def_list[5].rstrip("]")
            self.var_val.setText(var_val)
            self.var_name.setText(var_name)

class FunctionDialog(QDialog):
    def __init__(self, variables, functions=None):
        super().__init__()

        if functions is None:
            functions = {}
        self.setWindowTitle("Define functions")
        self.functions = functions

        # Create an autocompleter to autocomplete the variable names
        autocomplete_model = QStringListModel()
        autocomplete_model.setStringList(variables.keys())
        autocompleter = QCompleter()
        autocompleter.setModel(autocomplete_model)

        # Create the actual dialog which can be used to create the functions
        name_next_button = QPushButton("Finish")
        name_next_button.clicked.connect(self.accept)
        back_button = QPushButton("Back")
        back_button.clicked.connect(self.reject)

        # Add the next and back buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(name_next_button)
        button_layout.addWidget(back_button)

        flexible_grid = QHBoxLayout()
        self.function_list_widget = QListWidget()
        flexible_grid.addWidget(self.function_list_widget)
        self.function_ref_table = {}

        if self.functions:
            for func in self.functions:
                function_item = QListWidgetItem()
                function_item.setText(func + "\t => " + self.functions[func])
                self.function_ref_table[func] = function_item
                self.function_list_widget.addItem(function_item)

        # Create the edit fields to hold the variable names and functions
        edits = QGroupBox()
        edit_layout = QHBoxLayout()
        self.f_name = QLineEdit()
        self.f_form = QLineEdit()
        self.f_form.setCompleter(autocompleter)
        self.f_form.setMinimumWidth(400)

        edit_layout.addWidget(self.f_name)
        edit_layout.addWidget(self.f_form)
        self.f_form.setValidator(FunctionValidator(variables))
        self.function_list_widget.itemDoubleClicked.connect(self.update_functions)
        edits.setLayout(edit_layout)

        # Add buttons for adding and removing functions and connect them
        modify_layout = QHBoxLayout()
        add_button = QPushButton("Add Function")
        add_button.clicked.connect(self.add_function)
        remove_button = QPushButton("Remove Selected")
        remove_button.clicked.connect(partial(remove_selected, self.function_list_widget, self.functions))
        modify_layout.addWidget(add_button)
        modify_layout.addWidget(remove_button)

        # Create the layout for the entire dialog
        layout = QGridLayout()
        layout.addLayout(flexible_grid, 0, 0)
        layout.addWidget(edits, 1, 0)
        layout.addLayout(modify_layout, 2, 0)
        layout.addLayout(button_layout, 3, 0)

        self.setLayout(layout)

    def get_functions(self):
        return self.functions

    def add_function(self):
        # A function is valid if it is returned as such by the validator
        self.f_form.validator().set_confirmed(True)
        valid_function = self.f_form.hasAcceptableInput()
        # A name is valid as long as its not empty
        valid_name = not self.f_name.text().strip() == ""
        if valid_name and valid_function:
            if self.f_name.text() in self.functions:
                # Function already exists
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                msg.setText("The name you entered already exists, \nOverwrite?")
                msg.setWindowTitle("Name already exists")
                msg.setStandardButtons(QMessageBox.Yes)
                msg.addButton(QMessageBox.No)
                msg.setDefaultButton(QMessageBox.No)
                if msg.exec() == QMessageBox.No:
                    self.f_form.validator().set_confirmed(False)
                    return
                else:
                    # Remove existing function from dict to prepare for write
                    self.functions.pop(self.f_name.text())
                    # Update view accordingly
                    overwrite_item = self.function_ref_table[self.f_name.text()]
                    self.function_list_widget.takeItem(self.function_list_widget.row(overwrite_item))

            self.functions[self.f_name.text()] = self.f_form.text()
            self.function_list_widget.addItem(QListWidgetItem(self.f_name.text() + "\t => " + self.f_form.text()))
            self.f_form.validator().set_confirmed(False)
            self.f_form.clear()

    def update_functions(self):
        for selected in self.function_list_widget.selectedItems():
            self.function_list_widget.item(self.function_list_widget.row(selected))
            func = selected.text().split("=>")
            var_name = func[0].strip()
            var_form = func[1].strip()
            self.f_name.setText(var_name)
            self.f_form.setText(var_form)


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

def remove_selected(var_view, variables):
    # Removes the selected item from the specified widget and from the corresponding item:value dict
    for selected in var_view.selectedItems():
        var_view.takeItem(var_view.row(selected))
        var_name = selected.text().split("=>")[0].strip()
        variables.pop(var_name)
