""" Contains the definition of the side panel on the right hand side of the UI. This panel displays the relevant
    information for the model."""
from functools import partial

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QLinearGradient
from PyQt5.QtWidgets import QWidget, QGridLayout, QGroupBox, QLabel, QSlider, QHBoxLayout, QVBoxLayout, \
    QPushButton, QDialog, QGraphicsProxyWidget, QTextEdit, QDialogButtonBox, QLineEdit

from ceteris_paribus.gui.commands import DeleteCommand
from ceteris_paribus.gui.dialogs.var_dialog import VarDialog
from ceteris_paribus.gui.dialogs.function_dialog import FunctionDialog

import pyqtgraph as pg

class ContextPane(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.name_label = QLabel()
        self.local_outs = {}
        self.controller = controller

        self.context = QGridLayout()

        # Find the available screen geometry
        available_height = self.height()

        self.input_group = QGroupBox("Inputs")
        self.input_group.setFixedSize(300, (available_height / 2))

        self.context_group = QGroupBox("Context")
        self.context_group.setFixedSize(300, (available_height / 2))

        self.output_group = QGroupBox("Outputs")
        self.output_group.setFixedSize(300, (available_height / 2))

        color_group = QGroupBox("Color")
        color_group.setFixedSize(300, (available_height / 6))
        self.colorBar = pg.GradientWidget()
        color_layout = QGridLayout()
        color_layout.addWidget(self.colorBar)
        color_group.setLayout(color_layout)
        self.colorBar.loadPreset('cyclic')
        self.colorBar.sigGradientChangeFinished.connect(lambda : self.controller.update_colors())

        layout = QGridLayout()
        layout.addWidget(self.input_group)
        layout.addWidget(self.context_group)
        layout.addWidget(self.output_group)
        layout.addWidget(color_group)

        self.setLayout(layout)

    def reload(self):
        self.initialize_input()

        # Initialize the current organ being displayed in the model to be the first organ encountered in the list
        self.change_context_organ(list(self.controller.get_organs().values())[0])
        self.initialize_context()

        self.initialize_output()

    def initialize_input(self):
        layout = QVBoxLayout()

        glob_button = QPushButton("View global inputs")
        glob_button.clicked.connect(self.show_globals)
        layout.addWidget(glob_button)

        slider_layout = QGridLayout()

        global_params = self.controller.get_global_param_ranges()
        for index, param_name in enumerate(global_params):
            slider_layout.addWidget(QLabel(param_name), index+1, 0)
            slider = QSlider(Qt.Horizontal)
            slider.setMinimum(global_params[param_name][0])
            slider.setMaximum(global_params[param_name][1])
            slider.setValue(global_params[param_name][2])
            slider.valueChanged.connect(partial(self.controller.param_changed, param_name, slider))
            slider_layout.addWidget(slider, index+1, 1)
        slider_layout.setRowStretch(2, 500)
        layout.addLayout(slider_layout)
        self.input_group.setLayout(layout)

    def initialize_context(self):
        layout = QVBoxLayout()
        layout.addWidget(self.name_label)

        button_layout = QGridLayout()

        var_button = QPushButton("Local values")
        var_button.clicked.connect(self.show_locals)
        button_layout.addWidget(var_button, 0, 0)

        func_button = QPushButton("Functions")
        func_button.clicked.connect(self.show_local_funcs)
        button_layout.addWidget(func_button, 0, 1)

        out_button = QPushButton("Outputs")
        out_button.clicked.connect(self.show_outs)
        button_layout.addWidget(out_button, 1, 0)

        del_button = QPushButton("Delete")
        del_button.clicked.connect(self.delete_organ)
        button_layout.addWidget(del_button, 1, 1)
        layout.addLayout(button_layout)

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
                value_label = QLabel(str(round(slider.value(), 2)))
                slider.valueChanged.connect(partial(self.controller.organ_local_changed, name, slider, value_label))
                layout.addWidget(slider, index, 1)
                layout.addWidget(value_label, index, 2)
        edit_button = QPushButton('Edit')
        edit_button.clicked.connect(partial(self.edit_locals, dialog))
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

    def show_local_funcs(self):
        dialog = QDialog()
        layout = QGridLayout()
        dialog.setWindowTitle("Functions")
        if self.current_organ.get_funcs():
            for index, func in enumerate(self.current_organ.get_funcs()):
                layout.addWidget(QLabel(func + ":"), index, 0)
                layout.addWidget(QLabel(str(self.current_organ.get_funcs()[func])), index, 1)
        else:
            layout.addWidget(QLabel("No functions have been defined for this organ"))
        edit_button = QPushButton('Edit')
        edit_button.clicked.connect(partial(self.edit_functions, dialog))
        layout.addWidget(edit_button)
        dialog.setLayout(layout)
        dialog.exec()

    def show_global_funcs(self):
        dialog = QDialog()
        layout = QGridLayout()
        dialog.setWindowTitle("Global functions")
        functions_dict = self.controller.get_functions()
        for index, func in enumerate(functions_dict):
            layout.addWidget(QLabel(func), index, 0)
            layout.addWidget(QLabel(functions_dict[func]), index, 1)
        dialog.setLayout(layout)
        dialog.exec()

    def modify_global_funcs(self):
        dialog = QDialog()
        layout = QGridLayout()
        dialog.setWindowTitle("Global functions")
        functions_dict = self.controller.get_functions()
        for func in functions_dict:
            button = QPushButton(func)
            button.clicked.connect(partial(self.change_single_function, func, functions_dict[func]))
            layout.addWidget(button)
        dialog.setLayout(layout)
        dialog.exec()

    def change_single_function(self, f_name, f_string):
        dialog = QDialog()
        layout = QGridLayout()
        dialog.setWindowTitle("Modify " + f_name)

        new_func = QLineEdit()
        new_func.setText(f_string)
        layout.addWidget(new_func)

        button_layout = QHBoxLayout()
        accept_button = QPushButton('Accept')
        accept_button.clicked.connect(dialog.accept)
        button_layout.addWidget(accept_button)
        cancel_button = QPushButton('Cancel')
        cancel_button.clicked.connect(dialog.reject)
        button_layout.addWidget(cancel_button)
        layout.addItem(button_layout)

        dialog.setLayout(layout)
        if dialog.exec():
            self.controller.model.add_global_func(f_name, new_func.text())

    def show_outs(self):
        dialog = QDialog()
        layout = QGridLayout()
        dialog.setWindowTitle("Outputs")
        if self.current_organ.get_funcs():
            for index, func in enumerate(self.current_organ.get_funcs()):
                layout.addWidget(QLabel(func + ":"), index, 0)
                layout.addWidget(QLabel(str(round(self.current_organ.defined_variables[func], 2))), index, 1)
        else:
            layout.addWidget(QLabel("No outputs can be displayed for this organ"))
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

    def edit_locals(self, previous_dialog):
        dialog = VarDialog(self.current_organ.get_local_ranges())

        if dialog.exec_():
            # Close the previous dialogs and start a new one, showing the updated locals
            previous_dialog.accept()
            self.show_locals()

    def edit_functions(self, previous_dialog):
        dialog = FunctionDialog(self.current_organ.get_defined_variables(), self.current_organ.get_funcs())

        if dialog.exec_():
            previous_dialog.accept()
            self.show_local_funcs()

    def initialize_output(self):
        outputs = self.controller.get_outputs()
        layout = QGridLayout()

        view_outs = QPushButton("View global functions")
        view_outs.clicked.connect(lambda : self.show_global_funcs())
        layout.addWidget(view_outs, 0, 0)

        modify_outs = QPushButton("Modify global functions")
        modify_outs.clicked.connect(lambda : self.modify_global_funcs())
        layout.addWidget(modify_outs, 0, 1)

        for index, out_name in enumerate(outputs):
            out_button = QPushButton(out_name)
            out_button.clicked.connect(partial(self.controller.set_colors_for_global, out_name))
            layout.addWidget(out_button, index+1, 0)
            self.local_outs[out_name] = QLabel(str(round(outputs[out_name], 2)))
            self.local_outs[out_name].setStyleSheet("QLabel { background-color : white; color : blue; }")
            layout.addWidget(self.local_outs[out_name], index+1, 1)
        self.output_group.setLayout(layout)

    def update_output(self):
        outputs = self.controller.get_outputs()
        for local_out_val in self.local_outs:
            self.local_outs[local_out_val].setText(str(round(outputs[local_out_val],2)))
            if self.controller.current_global == local_out_val:
                # If the output of the currently selected value is changed we update the color schemes
                self.controller.set_colors_for_global(local_out_val)