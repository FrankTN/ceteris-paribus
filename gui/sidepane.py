""" Contains the definition of the side panel on the right hand side of the UI. This panel displays the relevant
    information for the model."""
from functools import partial

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtWidgets import QWidget, QGridLayout, QGroupBox, QLabel, QSlider, QHBoxLayout, QVBoxLayout, \
    QPushButton, QDialog, QListWidgetItem, QListWidget, QLineEdit

from gui.commands import DeleteCommand


class ContextPane(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.local_outs = {}
        self.controller = controller

        self.context = QGridLayout()

        # Find the available screen geometry
        available_height = self.height()

        self.input_group = QGroupBox("Inputs")
        self.input_group.setFixedSize(300, (available_height / 2))
        self.set_input()

        self.context_group = QGroupBox("Context")
        self.context_group.setFixedSize(300, (available_height / 2))
        self.initialize_context()
        self.change_context_organ(list(controller.get_model().organs.values())[0])

        self.output_group = QGroupBox("Outputs")
        self.output_group.setFixedSize(300, (available_height / 2))
        self.initialize_output()

        layout = QGridLayout()
        self.context_group.setLayout(self.context)
        layout.addWidget(self.input_group)
        layout.addWidget(self.context_group)
        layout.addWidget(self.output_group)

        self.setLayout(layout)

    def set_input(self):
        layout = QGridLayout()
        global_params = self.controller.get_global_param_ranges()
        for index, param_name in enumerate(global_params):
            layout.addWidget(QLabel(param_name), index, 0)
            slider = QSlider(Qt.Horizontal)
            slider.setMinimum(global_params[param_name][0])
            slider.setMaximum(global_params[param_name][1])
            slider.setValue(global_params[param_name][2])
            slider.valueChanged.connect(partial(self.controller.param_changed, param_name, slider))
            layout.addWidget(slider, index, 1)
        layout.setRowStretch(2, 500)
        self.input_group.setLayout(layout)

    def initialize_context(self):
        layout = QVBoxLayout()
        self.name_label = QLabel()
        layout.addWidget(self.name_label)

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

        self.context_group.setLayout(layout)

    def change_context_organ(self, organ):
        self.current_organ = organ
        self.name_label.setText(organ.get_name())

    def show_locals(self):
        dialog = QDialog()
        dialog.setWindowTitle("Local values")
        layout = QGridLayout()

        for index, name in enumerate(self.current_organ.get_local_ranges()):
            # TODO make into sliders with values
            assert '__builtins__' not in self.current_organ.get_local_ranges()
            if name != '__builtins__':
                layout.addWidget(QLabel(name), index, 0)
                slider = QSlider(Qt.Horizontal)
                slider.setMinimum(self.current_organ.get_local_ranges()[name][0])
                slider.setMaximum(self.current_organ.get_local_ranges()[name][1])
                slider.setValue(self.current_organ.get_local_ranges()[name][2])
                value_label = QLabel(str(slider.value()))
                slider.valueChanged.connect(partial(self.controller.organ_local_changed, name, slider, value_label))
                layout.addWidget(slider, index, 1)
                layout.addWidget(value_label, index, 2)
        edit_button = QPushButton('Edit')
        edit_button.clicked.connect(self.edit_locals)
        layout.addWidget(edit_button, len(self.current_organ.get_local_ranges()), 0)
        dialog.setLayout(layout)
        dialog.exec_()

    def show_globals(self):
        dialog = QDialog()
        dialog.setWindowTitle("Globals")
        layout = QGridLayout()
        for index, val in enumerate(self.current_organ.get_globals()):
            layout.addWidget(QLabel(val), index, 0)
            layout.addWidget(QLabel(str(self.current_organ.get_globals()[val])), index, 1)
        dialog.setLayout(layout)
        dialog.exec_()

    def show_funcs(self):
        dialog = QDialog()
        layout = QGridLayout()
        dialog.setWindowTitle("Functions")
        for index, func in enumerate(self.current_organ.get_funcs()):
            layout.addWidget(QLabel(func + ":"), index, 0)
            layout.addWidget(QLabel(str(self.current_organ.get_funcs()[func])), index, 1)
        dialog.setLayout(layout)
        dialog.exec_()

    def show_outs(self):
        dialog = QDialog()
        layout = QGridLayout()
        dialog.setWindowTitle("Outputs")
        for index, func in enumerate(self.current_organ.get_funcs()):
            layout.addWidget(QLabel(func + ":"), index, 0)
            layout.addWidget(QLabel(str(self.current_organ.defined_variables[func])), index, 1)
        dialog.setLayout(layout)
        dialog.exec_()

    def delete_organ(self):
        dialog = QDialog()
        dialog.setWindowTitle("Delete " + self.current_organ.get_name() + "?")

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
            # Create the undoable command of deleting the current organ
            command = DeleteCommand(self.controller, self.current_organ)
            # Push the command on the undo stack
            self.controller.get_undo_stack().push(command)

    def edit_locals(self):
        dialog = QDialog()
        dialog.setWindowTitle("Edit local values")
        layout = QGridLayout()
        self.locals_list = QListWidget()
        ranges = self.current_organ.get_local_ranges()
        for item in ranges:
            list_item = QListWidgetItem()
            var_range = ranges[item]
            list_item.setText(item + "\t => [min: " + str(var_range[0]) + ", max: " + str(var_range[1]) + ", val: " +
                              str(var_range[2]) + "]")
            self.locals_list.addItem(list_item)
        layout.addWidget(self.locals_list)

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
        del_button.clicked.connect(partial(self.remove_selected, self.locals_list, self.current_organ.get_local_ranges()))
        edits.addWidget(add_button)
        edits.addWidget(del_button)
        edit_group.setLayout(edits)
        layout.addWidget(edit_group)

        dialog.setLayout(layout)
        dialog.exec_()

    def initialize_output(self):
        outputs = self.controller.model.get_outputs()
        layout = QGridLayout()
        for index, out_name in enumerate(outputs):
            labels = QHBoxLayout()
            out_button = QPushButton(out_name)
            out_button.clicked.connect(partial(self.controller.set_colors_for_global, out_name))
            labels.addWidget(out_button)
            self.local_outs[out_name] = QLabel(str(outputs[out_name]))
            labels.addWidget(self.local_outs[out_name])
            layout.addLayout(labels, index, 0)
        self.output_group.setLayout(layout)

    def update_output(self):
        outputs = self.controller.model.get_outputs()
        for local_out_val in self.local_outs:
            self.local_outs[local_out_val].setText(str(outputs[local_out_val]))
