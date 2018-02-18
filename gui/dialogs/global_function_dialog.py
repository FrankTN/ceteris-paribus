from PyQt5.QtWidgets import QDialog, QLineEdit, QComboBox, QPushButton, QGridLayout


class GlobalFunctionDialog(QDialog):

    def __init__(self, controller, **kwargs):
        super().__init__(**kwargs)
        self.controller = controller

        layout = QGridLayout()

        function_edit = QLineEdit()
        layout.addWidget(function_edit)

        organs = self.controller.get_organs()
        organ_selector = QComboBox()
        organ_selector.addItems(organs)

        add_var_button = QPushButton("Add")
        layout.addWidget(add_var_button)

        layout.addWidget(organ_selector)

        variable_selector = QComboBox()
        organ_selector.currentIndexChanged.connect(
            lambda: self.update_variables_in_combobox(organ_selector.currentText(), organs, variable_selector))

        layout.addWidget(variable_selector)
        self.setLayout(layout)

    def update_variables_in_combobox(self, newItem, organs, box):
        box.clear()
        box.addItems(organs[newItem].get_local_vals())
