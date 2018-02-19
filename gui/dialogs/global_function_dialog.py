from functools import partial

from PyQt5.QtWidgets import QDialog, QLineEdit, QComboBox, QPushButton, QGridLayout, QLabel, QGroupBox, QHBoxLayout, \
    QVBoxLayout

from ceteris_paribus.gui.validator import GlobalFunctionValidator


class GlobalFunctionDialog(QDialog):

    def __init__(self, controller, func_name, **kwargs):
        super().__init__(**kwargs)
        self.controller = controller
        function = self.controller.get_functions()[func_name]

        self.string_representation = self.parse_function(function)
        print(self.string_representation)

        # The main layout of the dialog
        layout = QVBoxLayout()

        # The function layout displays the function currently being worked on
        function_layout = QHBoxLayout()
        name_label = QLabel('TEST')
        function_layout.addWidget(name_label)

        self.function_edit = QLineEdit()
        self.function_edit.setReadOnly(True)
        self.function_edit.setText(' '.join(self.string_representation))
        self.function_edit.setValidator(GlobalFunctionValidator())
        function_layout.addWidget(self.function_edit)

        layout.addItem(function_layout)

        lower_layout = QHBoxLayout()
        lower_layout.addStretch()

        operator_layout = QGridLayout()
        operators = QGroupBox('Operators')
        add = QPushButton('+')
        add.clicked.connect(partial(self.add_word, '+'))
        operator_layout.addWidget(add, 0, 0)
        min = QPushButton('-')
        min.clicked.connect(partial(self.add_word, '-'))
        operator_layout.addWidget(min, 0, 1)
        mul = QPushButton('*')
        mul.clicked.connect(partial(self.add_word, '*'))
        operator_layout.addWidget(mul, 1, 0)
        div = QPushButton('/')
        div.clicked.connect(partial(self.add_word, '/'))
        operator_layout.addWidget(div, 1, 1)
        operators.setLayout(operator_layout)
        lower_layout.addWidget(operators)

        button_box = QGroupBox('Buttons')
        button_layout = QGridLayout()

        organs = self.controller.get_organs()
        organ_selector = QComboBox()
        organ_selector.addItems(organs)

        button_layout.addWidget(organ_selector, 0, 0)

        variable_selector = QComboBox()
        organ_selector.currentIndexChanged.connect(
            lambda: self.update_variables_in_combobox(organ_selector.currentText(), organs, variable_selector))
        button_layout.addWidget(variable_selector, 1, 0)
        organ_selector.currentIndexChanged.emit(0)

        add_val_button = QPushButton("Add")
        button_layout.addWidget(add_val_button, 0, 1)
        add_val_button.clicked.connect(
            lambda: self.add_combobox_value(organ_selector.currentText(), organs, variable_selector))

        rem_val_button = QPushButton("Remove")
        rem_val_button.clicked.connect(self.remove_word)
        button_layout.addWidget(rem_val_button, 1, 1)
        button_box.setLayout(button_layout)

        lower_layout.addWidget(button_box)
        layout.addItem(lower_layout)

        accept_or_cancel_layout = QHBoxLayout()
        accept_or_cancel_layout.addStretch()
        done_button = QPushButton("Done")
        done_button.clicked.connect(self.done)
        accept_or_cancel_layout.addWidget(done_button)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        accept_or_cancel_layout.addWidget(cancel_button)
        layout.addItem(accept_or_cancel_layout)

        self.setLayout(layout)

    def add_combobox_value(self, organ_name, organs, var_box):
        new_str = self.to_pretty_string(organ_name, var_box.currentText())

        self.add_word(new_str)
        print(organs[organ_name].get_local_ranges()[var_box.currentText()])

    def translate_arrow_word(self, word):
        # Translates a word of the form Organ->Variable to Organ
        organ_name, var_name = word.split('->')
        processed_word = organ_name + '.get_local_vals()' + '[\'' + var_name + '\']'
        return processed_word

    def remove_word(self):
        self.string_representation.pop()
        self.function_edit.setText(' '.join(self.string_representation))

    def add_word(self, word):
        self.string_representation.append(word)
        self.function_edit.setText(' '.join(self.string_representation))

    def add_value(self):
        pass

    def remove_value(self):
        pass

    def update_variables_in_combobox(self, newItem, organs, box):
        box.clear()
        box.addItems(organs[newItem].get_local_vals())

    def to_pretty_string(self, organ_name, organ_var):
        # Breakdown is a list of two elements, the organ name followed by the variable name
        pretty_string = organ_name + '->' + organ_var.strip('[\'').strip('\']')
        return pretty_string

    def parse_function(self, func):
        # Any well-formed function consists of data accesses and operations using this data. We have a global namespace,
        # and a list of organs.
        print(func.split())
        tokens = func.split()
        representation = []
        for token in tokens:
            if token in ['+','-','*','/']:
                # We have reached an operator
                representation.append(token)

            elif '.get_local_vals()' in token:
                # We have reached a statement of the form {Organ name}.get_local_vals()['{Variable name}']
                breakdown = token.split('.get_local_vals()')
                pretty_string = self.to_pretty_string(breakdown[0], breakdown[1])
                representation.append(pretty_string)
            else:
                # We are dealing with a global variable
                representation.append(token)

        return representation