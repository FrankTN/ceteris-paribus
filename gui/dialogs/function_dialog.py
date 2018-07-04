""" This module defines the function dialog class, which is created and executed when the user wants to view the
    functions defined for an organ."""
from functools import partial

from PyQt5.QtCore import QStringListModel
from PyQt5.QtWidgets import QDialog, QCompleter, QPushButton, QHBoxLayout, QListWidget, QListWidgetItem, QLineEdit, \
    QGroupBox, QGridLayout, QMessageBox, QComboBox

from ceteris_paribus.gui.dialogs.db_dialogs import remove_selected
from ceteris_paribus.gui.validator import LocalFunctionValidator


class FunctionDialog(QDialog):
    """ A class for viewing and modifying the functions in an organ. """

    def __init__(self, variables, organ_name, functions=None):
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

        # Create the actual dialogs which can be used to create the functions
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
        function_group = QGroupBox()
        group_layout = QGridLayout()
        edit_layout = QHBoxLayout()
        group_layout.addItem(edit_layout)
        horizontal_bar = QHBoxLayout()
        horizontal_bar.addStretch()
        group_layout.addItem(horizontal_bar)
        self.f_name = QLineEdit()
        self.f_form = QLineEdit()
        self.f_form.setCompleter(autocompleter)
        self.f_form.setMinimumWidth(400)

        add_var_button = QPushButton("Add var")
        add_var_button.clicked.connect(self.add_var)
        horizontal_bar.addWidget(add_var_button)
        self.var_list = QComboBox()
        self.var_list.addItems(variables.keys())
        horizontal_bar.addWidget(self.var_list)

        edit_layout.addWidget(self.f_name)
        edit_layout.addWidget(self.f_form)
        try:
            variable_values = {}
            for k, v in variables.items():
                variable_values[k] = v[2]
        except TypeError:
            # Encountering a type error means that we dont have a range
            variable_values = variables
        self.f_form.setValidator(LocalFunctionValidator(variable_values, organ_name))
        self.function_list_widget.itemDoubleClicked.connect(self.fill_edits)
        function_group.setLayout(group_layout)

        # Add buttons for adding and removing functions and connect them
        modify_layout = QHBoxLayout()
        add_button = QPushButton("Add Function")
        add_button.clicked.connect(self.add_function)
        remove_button = QPushButton("Remove Selected")
        remove_button.clicked.connect(partial(remove_selected, self.function_list_widget, self.functions))
        modify_layout.addWidget(add_button)
        modify_layout.addWidget(remove_button)

        # Create the layout for the entire dialogs
        layout = QGridLayout()
        layout.addLayout(flexible_grid, 0, 0)
        layout.addWidget(function_group, 1, 0)
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
        valid_name = self.f_name.text().isidentifier()
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
            item = QListWidgetItem(self.f_name.text() + "\t => " + self.f_form.text())
            self.function_ref_table[self.f_name.text()] = item
            self.function_list_widget.addItem(item)
            self.f_form.validator().set_confirmed(False)
            self.f_form.clear()
        else:
            # Either the name, the function or both are invalid. We respond accordingly by creating a messagebox and
            # filling it with a message
            self.f_form.validator().confirmed = False
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            if not valid_name and not valid_function:
                msg.setText("The name you used is not valid and the function cannot be "
                            "properly resolved")
            elif not valid_name:
                msg.setText("The name you used for the function is not valid")
            else:
                msg.setText("The variables in the function cannot be resolved, make sure they are defined")
            msg.setWindowTitle("Unable to create function")
            if msg.exec():
                return

    def add_var(self):
        append_text = self.var_list.currentText()
        base_text = self.f_form.text()
        self.f_form.setText(base_text + append_text)

    def fill_edits(self):
        # Filling the edits mean we obtain the selected value from the selected items and enter its values in their
        # respective textedits in the UI
        for selected in self.function_list_widget.selectedItems():
            self.function_list_widget.item(self.function_list_widget.row(selected))
            func = selected.text().split("=>")
            var_name = func[0].strip()
            var_form = func[1].strip()
            self.f_name.setText(var_name)
            self.f_form.setText(var_form)
