""" The controller acts as a layer handling communication between the GUI, the model and the database. """
#TODO this will be refactored into multiple smaller parts
import sys

from PyQt5.QtCore import QPointF
from PyQt5.QtWidgets import QApplication, QUndoStack

from db.db_dumper import dump_model
from gui.dialogs import select_db_dialog
from gui.graph_editor import GraphWindow
from gui.graph_scene import GraphScene
from model.globalmodel import GlobalModel


class Controller(object):

    def __init__(self):
        # Create an undo stack
        self.undo_stack = QUndoStack()
        # First we ask the user to select a database
        self.db = select_db_dialog()
        # Next, we create a model based on the database
        self.model = GlobalModel(self)
        # Finally, a UI is instantiated based on the current model
        self.ui = GraphWindow(self)
        # The context pane remains empty for now
        self.context_pane = self.ui.context

    def change_context_organ(self, organ):
        # Change the organ being displayed in the context menu on the right dock
        self.context_pane.change_context_organ(organ)

    def open_new_db(self):
        # Change to a new database, opens a UI dialog
        self.db = select_db_dialog()
        self.model = GlobalModel(self)
        # After changing the model and the database inside the controller, we ask the UI to update itself

    def get_model(self):
        return self.model

    def get_db(self):
        return self.db

    def get_global_param_ranges(self):
        # This function provides a layer of abstraction so other objects do not need to know about the existence of the
        # model. Note that the value returned is a dict where the values are lists of [min, max, val] defining the
        # ranges of the parameter
        return self.model.get_global_param_ranges()

    def get_global_param_values(self):
        # An abstraction from the model. Note that the value returned is a dict containing the values of the parameters
        # without the ranges
        return self.model.get_global_param_values()

    def param_changed(self, name: str, slider):
        # Another relay method to ensure the model is only used by the controller
        self.model.param_changed(name, slider)
        self.context_pane.update_output()

    def organ_local_changed(self, name: str, slider, label):
        # If the user changes a local value in an organ, this function is called. We change the local value and update
        # the UI accordingly
        organ = self.context_pane.current_organ
        organ.local_changed(name, slider)
        label.setText(str(slider.value()))
        self.context_pane.update_output()

    def set_colors_for_global(self, name: str):
        self.current_global = name
        # If we select a global value to visualize, this function updates the nodes involved so we can see how far each
        # node is in their range with respect to this value
        color_scheme_names = self.get_model().color_schemes[name]
        for organ in self.get_model().organs.values():
            if organ.get_name() in color_scheme_names:
                range = organ.get_local_ranges()[color_scheme_names[organ.get_name()]]
                controller.ui.scene.items[organ.get_name()].set_color(range)
            else:
                controller.ui.scene.items[organ.get_name()].set_gray()
        self.ui.scene.update()

    def add_organ(self, pos: QPointF, organ_name: str, variables: dict, funcs: dict, edges: list):
        # Adds an organ to the model object. We need to wrap all information in an organ_info dict because of the way
        # the database handling system works.
        organ_info = {}
        position = [pos.x(), pos.y()]
        organ_info['name'] = organ_name
        organ_info['variables'] = variables
        organ_info['functions'] = funcs
        added_organ = self.model.add(organ_info, position)
        self.ui.scene.add_organ_node(added_organ, edges)
        self.ui.scene.update()
        return added_organ

    def remove_organ(self, organ):
        # Removes an organ from the model and the UI
        self.model.remove(organ)
        self.ui.get_scene().remove_organ_node(organ)

    def get_undo_stack(self):
        return self.undo_stack

if __name__ == "__main__":
    # The starting point for the entire program, creates a QApplication and a controller.
    app = QApplication(sys.argv)
    controller = Controller()
    sys.exit(app.exec_())
