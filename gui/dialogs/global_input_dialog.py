from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtWidgets import QDialog, QGridLayout, QGroupBox, QLineEdit, QLabel, QPushButton, QHBoxLayout


class GlobalInputDialog(QDialog):

    def __init__(self, controller, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.controller = controller
        self.min = float()
        self.val = float()
        self.max = float()

        layout = QGridLayout()

        edit_group = QGroupBox()
        edits = QGridLayout()
        edits.addWidget(QLabel("Input name"), 0, 0)
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

        edit_group.setLayout(edits)

        layout.addWidget(edit_group, 0, 0)

        button_layout = QHBoxLayout()
        accept_button = QPushButton("Accept")
        accept_button.clicked.connect(self.verify)
        button_layout.addWidget(accept_button)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout, 1, 0)

        self.setLayout(layout)

    def verify(self):
        self.min = float(self.var_min.text())
        self.val = float(self.var_val.text())
        self.max = float(self.var_max.text())
        if self.var_name:
            if self.min < self.val < self.max:
                self.accept()

