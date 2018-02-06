from functools import partial

from PyQt5.QtCore import QStringListModel
from PyQt5.QtWidgets import QDialog, QCompleter, QPushButton, QHBoxLayout, QListWidget, QListWidgetItem, QLineEdit, \
    QGroupBox, QGridLayout, QMessageBox

from ceteris_paribus.gui.dialogs.db_dialogs import remove_selected
from ceteris_paribus.gui.validator import FunctionValidator


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

        # Create the layout for the entire dialogs
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
            item = QListWidgetItem(self.f_name.text() + "\t => " + self.f_form.text())
            self.function_ref_table[self.f_name.text()] = item
            self.function_list_widget.addItem(item)
            self.f_form.validator().set_confirmed(False)
            self.f_form.clear()
        else:
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


    def update_functions(self):
        for selected in self.function_list_widget.selectedItems():
            self.function_list_widget.item(self.function_list_widget.row(selected))
            func = selected.text().split("=>")
            var_name = func[0].strip()
            var_form = func[1].strip()
            self.f_name.setText(var_name)
            self.f_form.setText(var_form)