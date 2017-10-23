from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QHBoxLayout, QPushButton, QGridLayout, QLabel, QLineEdit, QFileDialog, QSlider
from tinydb import TinyDB


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


class InputSettingsDialog(QDialog):
    def __init__(self, model):
        super().__init__()
        self.setWindowTitle("Model Input")
        layout = QGridLayout()
        for index, val in enumerate(model.get_params()):
            layout.addWidget(QLabel(val), index, 0)
            slider = QSlider(Qt.Horizontal)
            slider.setMinimum(model.get_params()[val][0])
            slider.setMaximum(model.get_params()[val][1])
            slider.setValue(model.get_params()[val][2])
            layout.addWidget(slider, index, 1)
            slider.valueChanged.connect(lambda: model.param_changed(val, slider.value()))
        self.setLayout(layout)


class OrganSettingsDialog(QDialog):
    def __init__(self, organ):
        super().__init__()
        self.setWindowTitle(organ.get_name())
        layout = QGridLayout()
        for index, val in enumerate(organ.get_vars()):
            #TODO find a more elegant way of dealing with the builtins appearing
            if val != '__builtins__':
                print("val is " + str(val))
                layout.addWidget(QLabel(val), index, 0)
                layout.addWidget(QLabel(str(organ.get_vars()[val])), index, 1)
        self.setLayout(layout)


def open_db():
    """ This function, which opens the database and connects it to the model is called before the UI can actually be
        used. """
    qfd = QFileDialog()
    qfd.setNameFilter("*.json")
    qfd.exec_()
    # We can only select a single file, therefore, we can always look at [0] without missing anything
    potential_db = qfd.selectedFiles()[0]

    try:
        return TinyDB(potential_db)
    except:
        raise ValueError("Unable to load database")
