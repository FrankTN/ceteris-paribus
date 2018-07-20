"""This module contains a definition of a class for selecting the source of an organ. This source can be seen as the
    organ from which the model receives its blood supply. In our code this means that the organ gets its local variables
    from the source."""
from PyQt5.QtWidgets import QDialog, QGridLayout, QListWidget, QListWidgetItem, QPushButton, QHBoxLayout


class SourceDialog(QDialog):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller

        self.setWindowTitle("Select sources")
        layout = QGridLayout()
        self.list_view = QListWidget()
        self.list_view.itemSelectionChanged.connect(self.validate_list)

        # We manually add an item for the global inputs
        input_widget = QListWidgetItem()
        input_widget.setText("Global Input")
        self.list_view.addItem(input_widget)

        organ_names = list(self.controller.get_organ_names())

        for item in organ_names:
            if item is not '__builtins__':
                widget = QListWidgetItem()
                widget.setText(item)
                self.list_view.addItem(widget)

        self.name_next_button = QPushButton("&Next")
        self.name_next_button.setEnabled(False)
        back_button = QPushButton("Back")

        self.name_next_button.clicked.connect(self.accept)
        back_button.clicked.connect(self.reject)

        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch()
        buttonLayout.addWidget(self.name_next_button)
        buttonLayout.addWidget(back_button)

        layout.addWidget(self.list_view)
        layout.addLayout(buttonLayout, 1, 0)
        self.setLayout(layout)

    def get_source(self):
        # Returns the names of the selected sources
        source_list = []
        for source_widget in self.list_view.selectedItems():
            source_list.append(source_widget.text())
        return source_list

    def validate_list(self):
        # This function enables the next button once items have been selected
        if self.list_view.selectedItems():
            self.name_next_button.setEnabled(True)
        else:
            self.name_next_button.setEnabled(False)

    def get_name(self):
        return self.name

    def get_variables(self):
        # Return the variables after making sure that the builtins module is not included
        self.flattened_vars.pop('__builtins__', None)
        return self.flattened_vars

    def get_funcs(self):
        return self.functions
