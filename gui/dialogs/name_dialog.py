""" This module defines the class for entering the name of a new node. A name is entered and it is validated. """
from PyQt5.QtWidgets import QDialog, QPushButton, QHBoxLayout, QLabel, QLineEdit, QGridLayout


class NameDialog(QDialog):
    def __init__(self):
        # In this init method we create a simple dialog containing a text edit and a few buttons
        super().__init__()

        self.next_button = QPushButton("&Next")
        self.next_button.setEnabled(False)
        cancel_button = QPushButton("Cancel")

        self.setWindowTitle("Set node name")
        name_layout = QHBoxLayout()
        name_label = QLabel("&Name:")
        self.name_field = QLineEdit()
        # Every time the text changes, it is validated
        self.name_field.textChanged.connect(self.validate_text_field)

        name_label.setBuddy(self.name_field)
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_field)

        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch()
        buttonLayout.addWidget(self.next_button)
        buttonLayout.addWidget(cancel_button)

        layout = QGridLayout()
        layout.addLayout(name_layout, 0, 0)
        layout.addLayout(buttonLayout, 2, 0, 1, 3)
        self.setLayout(layout)

        self.next_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)

    def validate_text_field(self):
        # Right now, all nonempty strings are considered to be valid, this might change later.
        if not self.isEmpty(self.name_field.text()):
            self.name = self.name_field.text()
            self.next_button.setEnabled(True)
        else:
            self.next_button.setEnabled(False)

    def isEmpty(self, string):
        return string.strip() is ""
