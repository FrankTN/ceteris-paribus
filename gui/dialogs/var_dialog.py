from functools import partial

from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtWidgets import QDialog, QGridLayout, QListWidget, QListWidgetItem, QGroupBox, QLabel, QLineEdit, \
    QPushButton, QHBoxLayout, QMessageBox

from ceteris_paribus.gui.dialogs.db_dialogs import remove_selected


class VarDialog(QDialog):
    def __init__(self, variables):
        super().__init__()
        self.setWindowTitle("Define variables")
        layout = QGridLayout()

        # First, add all previously defined variables to the list, this is empty if we are working on a new organ
        self.var_list_widget = QListWidget()
        self.var_ref_table = {}
        for var in variables:
            list_item = QListWidgetItem()
            var_range = variables[var]
            list_item.setText(var + "\t => [min: " + str(var_range[0]) + ", max: " + str(var_range[1]) + ", val: " +
                              str(var_range[2]) + "]")
            self.var_ref_table[var] = list_item
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
                else:
                    # Remove the previous entry
                    overwrite_item = self.var_ref_table[self.var_name.text()]
                    self.var_list_widget.takeItem(self.var_list_widget.row(overwrite_item))
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