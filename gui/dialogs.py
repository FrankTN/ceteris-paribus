""" This module contains code to create all dialogs used by the program"""
from functools import partial

from PyQt5.QtCore import Qt, QStringListModel
from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtWidgets import QDialog, QHBoxLayout, QPushButton, QGridLayout, QLabel, QLineEdit, QFileDialog, QSlider, \
    QVBoxLayout, QMessageBox, QListWidget, QListWidgetItem, QCompleter, QGroupBox
from tinydb import TinyDB

from gui.validator import FunctionValidator


class NewNodeDialog(QDialog):
    """ This class can be used when creating new nodes"""
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.variables = {}

        self.nextButton = QPushButton("&Next")
        self.nextButton.setEnabled(False)
        cancelButton = QPushButton("Cancel")

        self.nextButton.clicked.connect(self.set_source)
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
        buttonLayout.addWidget(self.nextButton)
        buttonLayout.addWidget(cancelButton)

        layout = QGridLayout()
        layout.addLayout(name_layout, 0, 0)
        layout.addLayout(buttonLayout, 2, 0, 1, 3)
        self.setLayout(layout)

    def validate_text_field(self):
        if not self.isEmpty(self.nameField.text()):
            self.name = self.nameField.text()
            self.nextButton.setEnabled(True)
        else:
            self.nextButton.setEnabled(False)

    def isEmpty(self, string: str):
        return string.strip() is ""

    def set_source(self):
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

        self.nextButton = QPushButton("&Next")
        self.nextButton.setEnabled(False)
        back_button = QPushButton("Back")

        self.nextButton.clicked.connect(self.define_variables)
        back_button.clicked.connect(self.src_dialog.reject)

        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch()
        buttonLayout.addWidget(self.nextButton)
        buttonLayout.addWidget(back_button)

        layout.addWidget(self.list_view)
        layout.addLayout(buttonLayout, 1, 0)
        self.src_dialog.setLayout(layout)
        self.src_dialog.exec_()

    def validate_list(self):
        # This function enables the next button once items have been selected
        if self.list_view.selectedItems():
            self.src_edge_item = self.list_view.selectedItems()
            self.nextButton.setEnabled(True)
        else:
            self.nextButton.setEnabled(False)

    def define_variables(self):
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
        del_button.clicked.connect(partial(self.remove_selected, self.var_view, self.variables))
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
        minimum = float(self.var_min.text())
        maximum = float(self.var_max.text())
        value = float(self.var_val.text())

        valid_name = not self.var_name.text().strip() == ""
        if valid_name and minimum <= value <= maximum:
            self.var_view.addItem(QListWidgetItem(self.var_name.text() + " => [min: " + str(minimum) + ", max: " +
                                                  str(maximum) + ", val: " + str(value) + "]"))
            self.variables[self.var_name.text()] = [minimum, maximum, value]
            self.var_name.clear()
            self.var_min.clear()
            self.var_max.clear()
            self.var_val.clear()

    def remove_selected(self, list_widget, value_dict):
        for selected in list_widget.selectedItems():
            list_widget.takeItem(list_widget.row(selected))
            var_name = selected.text().split("=>")[0].strip()
            value_dict.pop(var_name)


    def define_functions(self):
        selected_strings = self.list_view.selectedItems()
        self.sources = []
        organ_vars = []

        for organ_name_widget in selected_strings:
            if organ_name_widget.text() == "Global Input":
                organ_vars.append(self.controller.get_global_params())
            else:
                self.sources.append(self.controller.get_model().get_organs()[organ_name_widget.text()])
        organ_vars += [x.local_ranges() for x in self.sources]

        self.flattened_vars = {}
        for var_dict in organ_vars:
            self.flattened_vars = {**var_dict, **self.flattened_vars}

        self.flattened_vars.pop('__builtins__', None)
        self.flattened_vars = {**self.flattened_vars, **self.variables}
        # Concatenate the lists of keys, thus obtaining the variable names as strings
        organ_var_strings = self.flattened_vars.keys()

        autocomplete_model = QStringListModel()
        autocomplete_model.setStringList(organ_var_strings)
        autocompleter = QCompleter()
        autocompleter.setModel(autocomplete_model)

        self.fnc_dialog = QDialog()
        self.nextButton = QPushButton("Finish")
        self.nextButton.clicked.connect(self.finalize)
        back_button = QPushButton("Back")
        back_button.clicked.connect(self.fnc_dialog.reject)

        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch()
        buttonLayout.addWidget(self.nextButton)
        buttonLayout.addWidget(back_button)

        self.functions = {}

        flexible_grid = QHBoxLayout()
        self.function_list_widget = QListWidget()
        flexible_grid.addWidget(self.function_list_widget)

        edits = QHBoxLayout()
        self.f_name = QLineEdit()
        self.f_form = QLineEdit()
        self.f_form.setCompleter(autocompleter)
        edits.addWidget(self.f_name)
        edits.addWidget(self.f_form)
        self.f_form.setValidator(FunctionValidator(self.flattened_vars))
        add_button = QPushButton("Add Function")
        add_button.clicked.connect(self.addFunction)
        remove_button = QPushButton("Remove Selected")
        remove_button.clicked.connect(partial(self.remove_selected, self.function_list_widget, self.functions))
        edits.addWidget(add_button)
        edits.addWidget(remove_button)

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
        self.flattened_vars.pop('__builtins__', None)
        return self.flattened_vars

    def get_funcs(self):
        return self.functions



class InputSettingsDialog(QDialog):
    """ This dialog is linked to the special Input node. It contains widgets to change input values.
        Note that all communication with the model occurs through the controller."""
    def __init__(self, controller):
        super().__init__()
        self.setWindowTitle("Model Input")
        layout = QGridLayout()
        global_params = controller.get_global_params()
        for index, param_name in enumerate(global_params):
            layout.addWidget(QLabel(param_name), index, 0)
            slider = QSlider(Qt.Horizontal)
            slider.setMinimum(global_params[param_name][0])
            slider.setMaximum(global_params[param_name][1])
            slider.setValue(global_params[param_name][2])
            slider.valueChanged.connect(partial(controller.param_changed, param_name, slider))
            layout.addWidget(slider, index, 1)
        self.setLayout(layout)

    def propagate_change(self):
        sender = self.sender()

class OutputSettingsDialog(QDialog):
    def __init__(self, controller):
        super().__init__()
        self.setWindowTitle("Model Output")


class OrganSettingsDialog(QDialog):
    def __init__(self, organ, controller):
        super().__init__()
        self.setWindowTitle(organ.get_name())
        self.organ = organ
        self.controller = controller

        layout = QVBoxLayout()

        var_button = QPushButton("Local values")
        var_button.clicked.connect(self.show_locals)
        layout.addWidget(var_button)

        glob_button = QPushButton("Global values")
        glob_button.clicked.connect(self.show_globals)
        layout.addWidget(glob_button)

        func_button = QPushButton("Functions")
        func_button.clicked.connect(self.show_funcs)
        layout.addWidget(func_button)

        out_button = QPushButton("Outputs")
        out_button.clicked.connect(self.show_outs)
        layout.addWidget(out_button)

        del_button = QPushButton("Delete")
        del_button.clicked.connect(self.delete_organ)
        layout.addWidget(del_button)

        self.setLayout(layout)

    def delete_organ(self):
        dialog = QDialog()
        dialog.setWindowTitle("Delete " + self.organ.get_name() + "?")

        msg = QLabel("Are you sure you want to delete this organ?")
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        y_button = QPushButton("Yes")
        y_button.clicked.connect(dialog.accept)
        button_layout.addWidget(y_button)
        n_button = QPushButton("No")
        n_button.clicked.connect(dialog.reject)
        button_layout.addWidget(n_button)

        layout = QGridLayout()
        layout.addWidget(msg, 0, 0)
        layout.addLayout(button_layout, 1, 0)

        dialog.setLayout(layout)
        if dialog.exec_():
            self.controller.remove_organ(self.organ)

    def show_locals(self):
        dialog = QDialog()
        dialog.setWindowTitle("Local values")
        layout = QGridLayout()
        
        for index, val in enumerate(self.organ.local_ranges()):
            #TODO make into sliders with values
            assert '__builtins__' not in self.organ.local_ranges()
            if val != '__builtins__':
                layout.addWidget(QLabel(val), index, 0)
                slider = QSlider(Qt.Horizontal)
                slider.setMinimum(self.organ.local_ranges()[val][0])
                slider.setMaximum(self.organ.local_ranges()[val][1])
                slider.setValue(self.organ.local_ranges()[val][2])
                layout.addWidget(slider, index, 1)
                self.setLayout(layout)

        dialog.setLayout(layout)
        dialog.exec_()

    def show_globals(self):
        dialog = QDialog()
        dialog.setWindowTitle("Globals")
        layout = QGridLayout()
        for index, val in enumerate(self.organ.get_globals()):
            layout.addWidget(QLabel(val), index, 0)
            layout.addWidget(QLabel(str(self.organ.get_globals()[val])), index, 1)
        dialog.setLayout(layout)
        dialog.exec_()

    def show_funcs(self):
        dialog = QDialog()
        layout = QGridLayout()
        dialog.setWindowTitle("Functions")
        for index, func in enumerate(self.organ.get_funcs()):
            layout.addWidget(QLabel(func + ":"), index, 0)
            layout.addWidget(QLabel(str(self.organ.get_funcs()[func])), index, 1)
        dialog.setLayout(layout)
        dialog.exec_()

    def show_outs(self):
        dialog = QDialog()
        layout = QGridLayout()
        dialog.setWindowTitle("Outputs")
        for index, func in enumerate(self.organ.get_funcs()):
            layout.addWidget(QLabel(func + ":"), index, 0)
            layout.addWidget(QLabel(str(self.organ.defined_variables[func])), index, 1)
        dialog.setLayout(layout)
        dialog.exec_()

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
