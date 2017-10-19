from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QHBoxLayout, QPushButton, QGridLayout, QLabel, QLineEdit


class NewNodeDialog(QDialog):
    def __init__(self):
        super().__init__()

        okButton = QPushButton("&OK")
        cancelButton = QPushButton("Cancel")

        okButton.clicked.connect(self.accept)
        cancelButton.clicked.connect(self.reject)
        self.setWindowTitle("Create new node")

        nameLabel = QLabel("&Name:")
        self.nameField = QLineEdit()
        nameLabel.setBuddy(self.nameField)

        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch()
        buttonLayout.addWidget(okButton)
        buttonLayout.addWidget(cancelButton)

        layout = QGridLayout()
        layout.addWidget(nameLabel, 0, 0)
        layout.addWidget(self.nameField, 0, 1)
        layout.addLayout(buttonLayout, 1, 0, 1, 3)
        self.setLayout(layout)

class OrganSettingsDialog(QDialog):
    def __init__(self):
        super().__init__()
