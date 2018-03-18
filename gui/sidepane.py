""" Contains the definition of the side panel on the right hand side of the UI. This panel displays the relevant
    information for the model."""
from functools import partial

import pyqtgraph as pg
from PyQt5.QtWidgets import QWidget, QGridLayout, QGroupBox, QLabel, QHBoxLayout, QVBoxLayout, \
    QPushButton, QDialog, QLineEdit, QComboBox, QFrame

from ceteris_paribus.gui.commands import DeleteCommand
from ceteris_paribus.gui.dialogs.function_dialog import FunctionDialog
from ceteris_paribus.gui.dialogs.global_function_dialog import GlobalFunctionDialog, parse_function
from ceteris_paribus.gui.dialogs.var_dialog import VarDialog
from ceteris_paribus.gui.visual_elements import FloatSlider


class ContextPane(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.current_organ = None
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
        self.output_grid_layout = QGridLayout()

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
            minimum = global_params[param_name][0]
            maximum = global_params[param_name][1]
            value = global_params[param_name][2]
            value_label = QLabel(str(round(value, 2)))
            target = partial(self.input_slider_changed, param_name, value_label)
            slider = FloatSlider(minimum, maximum, value, target)
            slider_layout.addWidget(slider, index+1, 1)
            slider_layout.addWidget(value_label, index+1, 2)
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
            assert '__builtins__' not in self.current_organ.get_local_ranges()
            if name != '__builtins__':
                layout.addWidget(QLabel(name), index, 0)
                minimum = self.current_organ.get_local_ranges()[name][0]
                maximum = self.current_organ.get_local_ranges()[name][1]
                value = self.current_organ.get_local_ranges()[name][2]
                value_label = QLabel(str(round(value, 2)))
                target = partial(self.controller.organ_local_changed, name, value_label)
                slider = FloatSlider(minimum, maximum, value, target)
                layout.addWidget(slider, index, 1)
                layout.addWidget(value_label, index, 2)
        edit_button = QPushButton('Edit')
        edit_button.clicked.connect(partial(self.edit_locals, dialog))
        layout.addWidget(edit_button, len(self.current_organ.get_local_ranges()), 0)
        dialog.setLayout(layout)
        dialog.exec_()

    def show_globals(self):
        print(self.controller.get_global_param_ranges())
        dialog = QDialog()
        dialog.setWindowTitle("Globals")
        layout = QGridLayout()
        for index, val in enumerate(self.current_organ.get_globals()):
            layout.addWidget(QLabel(val), index, 0)
            layout.addWidget(QLabel(str(round(self.current_organ.get_globals()[val],2))), index, 1)
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
        # This function creates a dialog for viewing and editing the global functions
        dialog = QDialog()

        layout = QGridLayout()
        dialog.setWindowTitle("Global functions")

        functions_dict = self.controller.get_global_functions()
        function_selector = QComboBox()
        function_selector.addItems(functions_dict)
        layout.addWidget(function_selector)

        buttons = QHBoxLayout()

        view_button = QPushButton('View')
        view_button.clicked.connect(partial(self.view_global_function, function_selector, functions_dict))
        buttons.addWidget(view_button)

        edit_button = QPushButton('Edit')
        edit_button.clicked.connect(partial(self.edit_global_function, function_selector, functions_dict))
        buttons.addWidget(edit_button)

        layout.addItem(buttons)

        new_remove_layout = QHBoxLayout()
        new_button = QPushButton('New')
        new_button.clicked.connect(self.new_global_function)
        new_remove_layout.addWidget(new_button)
        remove_button = QPushButton('Remove')
        remove_button.clicked.connect(partial(self.remove_global_function, function_selector))
        remove_button.clicked.connect(dialog.accept)
        new_remove_layout.addWidget(remove_button)

        layout.addItem(new_remove_layout)

        dialog.setLayout(layout)
        dialog.exec()

    def edit_global_function(self, func_combobox):
        dialog = GlobalFunctionDialog(self.controller, func_combobox.currentText())
        if dialog.exec():
            self.controller.add_global_function(dialog.func_name, dialog.reconstruction)
            print(dialog.reconstruction)

    def view_global_function(self, func_combobox, func_dict):
        dialog = QDialog()
        layout = QGridLayout()

        name = func_combobox.currentText()
        name_label = QLabel(name)
        layout.addWidget(name_label, 0, 0)
        line = QFrame()
        line.setFrameShape(QFrame.VLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line, 0, 1)


        func = parse_function(func_dict[name])
        str_label = QLabel(" ".join(func))
        layout.addWidget(str_label, 0, 2)
        dialog.setLayout(layout)
        dialog.exec()

    def new_global_function(self):
        dialog = GlobalFunctionDialog(self.controller)
        if dialog.exec():
            self.controller.add_global_function(dialog.func_name, dialog.reconstruction)

    def remove_global_function(self, selector):
        removable_func = selector.currentText()
        self.controller.remove_global_func(removable_func)
        self.reload_output_layout()

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
                layout.addWidget(QLabel(str(round(self.current_organ.get_defined_variables()[func], 2))), index, 1)
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
        dialog = FunctionDialog(self.current_organ.get_defined_variables(), self.current_organ.get_name(), self.current_organ.get_funcs())

        if dialog.exec_():
            previous_dialog.accept()
            self.show_local_funcs()

    def reload_output_layout(self):
        while not self.output_grid_layout.isEmpty():
            # Our first item is always the button
            item = self.output_grid_layout.takeAt(0)
            self.output_grid_layout.removeItem(item)
            if item.widget():
                item.widget().deleteLater()
        self.fill_output_grid()

    def fill_output_grid(self):
        outputs = self.controller.get_outputs()
        for index, out_name in enumerate(outputs):
            out_button = QPushButton(out_name)
            out_button.clicked.connect(partial(self.controller.set_colors_for_global, out_name))
            self.output_grid_layout.addWidget(out_button, index+1, 0)
            self.local_outs[out_name] = QLabel(str(round(outputs[out_name], 2)))
            self.local_outs[out_name].setStyleSheet("QLabel { background-color : white; color : blue; }")
            self.output_grid_layout.addWidget(self.local_outs[out_name], index+1, 1)
        self.output_group.update()

    def initialize_output(self):
        output_layout = QVBoxLayout()

        button_layout = QHBoxLayout()
        global_outs = QPushButton("Global functions")
        global_outs.clicked.connect(lambda : self.show_global_funcs())
        button_layout.addWidget(global_outs)

        self.fill_output_grid()

        output_layout.addLayout(button_layout)
        output_layout.addLayout(self.output_grid_layout)
        self.output_group.setLayout(output_layout)

    def update_output(self, target_label, new_out):
        if target_label is not None:
            target_label.setText(str(round(new_out,2)))
        outputs = self.controller.get_outputs()
        for local_out_val in self.local_outs:
            self.local_outs[local_out_val].setText(str(round(outputs[local_out_val],2)))
            if self.controller.current_global == local_out_val:
                # If the output of the currently selected value is changed we update the color schemes
                self.controller.set_colors_for_global(local_out_val)

    def input_slider_changed(self, name, label, value):
        # Change global parameter, call global param changed
        label.setText(str(round(value, 2)))
        self.controller.input_slider_changed(name, value)