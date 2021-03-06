from functools import partial

from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtWidgets import QDialog, QLineEdit, QComboBox, QPushButton, QGridLayout, QLabel, QGroupBox, QHBoxLayout, \
    QVBoxLayout

from ceteris_paribus.db.function_parser import EvalWrapper, ModelTransformer


operators = ['+', '-', '*', '/']

def translate_arrow_word(word):
    # Translates a word of the form Organ->Variable to Organ
    organ_name, var_name = word.split('->')
    processed_word = organ_name + '.get_defined_variables()' + '[\'' + var_name + '\']'
    return processed_word


def reconstruct_function(representation):
    result = ''
    for token in representation:
        if token in operators:
            # token is an operator
            result += token
        elif '->' in token:
            result += translate_arrow_word(token)
        else:
            result += token
        result += ' '
    return result


def to_pretty_string(organ_name, organ_var):
    # Breakdown is a list of two elements, the organ name followed by the variable name
    pretty_string = organ_name + '->' + organ_var.strip('[\'').strip('\']')
    return pretty_string


def parse_function(func):
    # Any well-formed function consists of data accesses and operations using this data. We have a global namespace,
    # and a list of organs.
    tokens = func.split()
    representation = []
    count = 0
    for token in tokens:
        if count == 4:
            # Once we count 4 tokens we append a newline and reset the counter
            representation.append('\n')
            count = 0
        if token in operators:
            # We have reached an operator
            representation.append(token)

        elif '.get_defined_variables()' in token:
            # We have reached a statement of the form {Organ name}.get_defined_variables()['{Variable name}']
            breakdown = token.split('.get_defined_variables()')
            pretty_string = to_pretty_string(breakdown[0], breakdown[1])
            representation.append(pretty_string)
        else:
            # We are dealing with a global variable
            representation.append(token)
        count += 1

    return representation


class GlobalFunctionDialog(QDialog):
    """ Dialog for interacting with the global functions. Precondition: all global functions defined so far are
        well-defined."""

    def __init__(self, controller, func_name='New_function', **kwargs):
        super().__init__(**kwargs)
        self.controller = controller
        functions = self.controller.get_global_functions().copy()
        self.func_name = func_name

        current_function = ''
        if func_name in functions:
            current_function = self.controller.get_global_functions()[func_name]
            functions.pop(self.func_name, None)

        accessible_vars = {**self.controller.get_organs(), **functions}
        self.evaluator = EvalWrapper(accessible_vars, ModelTransformer(accessible_vars))
        self.evaluator.set_function_name(func_name)

        self.list_representation = parse_function(current_function)

        # The main layout of the dialog
        layout = QVBoxLayout()

        # The function layout displays the function currently being worked on
        function_layout = QHBoxLayout()
        self.name_label = QPushButton(' ' + self.func_name + ' ')
        self.name_label.clicked.connect(self.change_func_name)
        function_layout.addWidget(self.name_label)

        self.function_edit = QLineEdit()
        self.function_edit.setText(' '.join(self.list_representation))
        function_layout.addWidget(self.function_edit)

        layout.addItem(function_layout)

        lower_layout = QHBoxLayout()
        lower_layout.addStretch()

        operator_layout = QGridLayout()
        operator_box = QGroupBox('Operators')
        add = QPushButton('+')
        add.clicked.connect(partial(self.add_word, ' + '))
        operator_layout.addWidget(add, 0, 0)
        min = QPushButton('-')
        min.clicked.connect(partial(self.add_word, ' - '))
        operator_layout.addWidget(min, 0, 1)
        mul = QPushButton('*')
        mul.clicked.connect(partial(self.add_word, ' * '))
        operator_layout.addWidget(mul, 1, 0)
        div = QPushButton('/')
        div.clicked.connect(partial(self.add_word, ' / '))
        operator_layout.addWidget(div, 1, 1)
        lpar = QPushButton('(')
        lpar.clicked.connect(partial(self.add_word, ' ( '))
        operator_layout.addWidget(lpar)
        rpar = QPushButton(')')
        rpar.clicked.connect(partial(self.add_word, ' ) '))
        operator_layout.addWidget(rpar)
        operator_box.setLayout(operator_layout)
        lower_layout.addWidget(operator_box)

        local_box = QGroupBox('Local outs')
        local_layout = QGridLayout()

        organs = self.controller.get_organs()
        organ_selector = QComboBox()
        organ_selector.addItems(organs)

        local_layout.addWidget(organ_selector, 0, 0)

        variable_selector = QComboBox()
        organ_selector.currentIndexChanged.connect(
            lambda: self.update_variables_in_combobox(organ_selector.currentText(), organs, variable_selector))
        local_layout.addWidget(variable_selector, 1, 0)
        organ_selector.currentIndexChanged.emit(0)

        add_val_button = QPushButton("Add")
        local_layout.addWidget(add_val_button, 2, 0)
        add_val_button.clicked.connect(
            lambda: self.add_combobox_value(organ_selector.currentText(), variable_selector))

        local_box.setLayout(local_layout)

        lower_layout.addWidget(local_box)

        global_box = QGroupBox('Global vars')
        global_layout = QGridLayout()
        global_selector = QComboBox()
        global_selector.addItems(functions)
        global_layout.addWidget(global_selector)
        global_add_button = QPushButton('Add')
        global_add_button.clicked.connect(lambda: self.add_word(global_selector.currentText()))
        global_layout.addWidget(global_add_button)
        global_box.setLayout(global_layout)

        lower_layout.addWidget(global_box)

        layout.addItem(lower_layout)

        rem_val_button = QPushButton("Remove")
        rem_val_button.clicked.connect(self.remove_word)
        #.addWidget(rem_val_button, 1, 1)

        accept_or_cancel_layout = QHBoxLayout()
        accept_or_cancel_layout.addStretch()
        done_button = QPushButton("Done")
        done_button.clicked.connect(self.check_if_done)
        accept_or_cancel_layout.addWidget(done_button)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        accept_or_cancel_layout.addWidget(cancel_button)
        layout.addItem(accept_or_cancel_layout)

        self.setLayout(layout)

    def change_func_name(self):
        dialog = QDialog()

        layout = QVBoxLayout()
        edit_layout = QHBoxLayout()
        name_label = QLabel('New Name')
        edit_layout.addWidget(name_label)
        new_name = QLineEdit()
        edit_layout.addWidget(new_name)
        layout.addItem(edit_layout)

        buttons = QHBoxLayout()
        buttons.addStretch()
        done = QPushButton('Accept')
        done.clicked.connect(dialog.accept)
        buttons.addWidget(done)
        cancel = QPushButton('Cancel')
        cancel.clicked.connect(dialog.reject)
        buttons.addWidget(cancel)
        layout.addItem(buttons)
        dialog.setLayout(layout)

        if dialog.exec():
            self.func_name = new_name.text()
            self.name_label.setText(' ' + self.func_name + ' ')

    def add_combobox_value(self, organ_name, var_box):
        if var_box.currentText():
            new_str = to_pretty_string(organ_name, var_box.currentText())
            self.add_word(new_str)

    def remove_word(self):
        self.list_representation = self.function_edit.text().split()
        if self.list_representation:
            self.list_representation.pop()
        self.function_edit.setText(' '.join(self.list_representation))

    def add_word(self, word):
        self.function_edit.setText(self.function_edit.text() + word)
        self.list_representation = self.function_edit.text().split()

    def check_if_done(self):
        self.list_representation = self.function_edit.text().split()
        self.reconstruction = reconstruct_function(self.list_representation)
        if self.reconstruction and self.controller.verify_function(self.reconstruction):
            self.accept()

    def update_variables_in_combobox(self, newItem, organs, box):
        box.clear()
        # We can only add an item if it has a name, therefore we check whether the string is not empty
        if newItem:
            box.addItems(organs[newItem].get_funcs())
