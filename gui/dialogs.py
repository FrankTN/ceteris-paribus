from functools import partial

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QHBoxLayout, QPushButton, QGridLayout, QLabel, QLineEdit, QFileDialog, QSlider, \
    QVBoxLayout
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
        for index, param_name in enumerate(model.get_params()):
            layout.addWidget(QLabel(param_name), index, 0)
            slider = QSlider(Qt.Horizontal)
            slider.setMinimum(model.get_params()[param_name][0])
            slider.setMaximum(model.get_params()[param_name][1])
            slider.setValue(model.get_params()[param_name][2])
            slider.valueChanged.connect(partial(model.param_changed, param_name, slider))
            layout.addWidget(slider, index, 1)
        self.setLayout(layout)

    def propagate_change(self):
        sender = self.sender()


class OrganSettingsDialog(QDialog):
    def __init__(self, organ):
        super().__init__()
        self.setWindowTitle(organ.get_name())
        self.organ = organ

        layout = QVBoxLayout()

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

        self.setLayout(layout)


    def show_locals(self):
        dialog = QDialog()
        dialog.setWindowTitle("Local values")
        layout = QGridLayout()
        for index, val in enumerate(self.organ.get_locals()):
            #TODO find a more elegant way of dealing with the builtins appearing
            #TODO make into sliders with values
            if val != '__builtins__':
                print("val is " + str(val))
                layout.addWidget(QLabel(val), index, 0)
                layout.addWidget(QLabel(str(self.organ.get_locals()[val])), index, 1)
        dialog.setLayout(layout)
        dialog.exec_()

    def show_globals(self):
        dialog = QDialog()
        dialog.setWindowTitle("Globals")
        layout = QGridLayout()
        for index, val in enumerate(self.organ.get_globals()):
            layout.addWidget(QLabel(val), index, 0)
            layout.addWidget(QLabel(str(self.organ.get_globals()[val])), index, 1)
        dialog.setLayout(layout)
        dialog.exec_()

    def show_funcs(self):
        dialog = QDialog()
        layout = QGridLayout()
        dialog.setWindowTitle("Functions")
        for index, func in enumerate(self.organ.get_funcs()):
            layout.addWidget(QLabel(func + ":"), index, 0)
            layout.addWidget(QLabel(str(self.organ.get_funcs()[func])), index, 1)
        dialog.setLayout(layout)
        dialog.exec_()

    def show_outs(self):
        dialog = QDialog()
        layout = QGridLayout()
        dialog.setWindowTitle("Outputs")
        for index, func in enumerate(self.organ.get_funcs()):
            layout.addWidget(QLabel(func + ":"), index, 0)
            layout.addWidget(QLabel(str(self.organ.defined_variables[func])), index, 1)
        dialog.setLayout(layout)
        dialog.exec_()

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
