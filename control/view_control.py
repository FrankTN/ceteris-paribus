from PyQt5.QtWidgets import QUndoStack, QGraphicsView

from ceteris_paribus.gui.graph_editor import GraphWindow


class ViewController(object):
    """ The ViewController is a class in the controller module, it contains those functions concerned with controlling
        the UI."""

    def __init__(self, global_control):
        self.global_control = global_control

        # Create an undo stack
        self.undo_stack = QUndoStack()
        # Finally, a UI is instantiated based on the current model
        self.ui = GraphWindow(self)
        # The context pane remains empty for now
        self.context_pane = self.ui.context
        self.current_global = None
        self.init_empty_model()

    def get_undo_stack(self):
        return self.undo_stack

    def add_organ(self, pos, organ_name, variables, funcs, edges):
        # Adds an organ to the model object. We need to wrap all information in an organ_info dict because of the way
        # the database handling system works.
        organ_info = {}
        position = [pos.x(), pos.y()]
        organ_info['name'] = organ_name
        organ_info['variables'] = variables
        organ_info['functions'] = funcs
        added_organ = self.global_control.get_model().add(organ_info, position)
        self.ui.scene.add_organ_node(added_organ, edges)
        self.ui.scene.update()
        self.ui.context.change_context_organ(added_organ)
        return added_organ

    def remove_organ(self, organ):
        # Removes an organ from the model and the UI
        self.global_control.get_model().remove(organ)
        self.ui.get_scene().remove_organ_node(organ)

    def update_colors(self):
        # This function is called when something changes in the color editor.
        if hasattr(self, 'current_global') and self.current_global is not None:
            self.set_colors_for_global(self.current_global)

    def get_global_param_ranges(self):
        return self.global_control.get_model().get_global_param_ranges()

    def get_model(self):
        return self.global_control.get_model()

    def get_global_funcs(self):
        return self.global_control.get_model().get_global_functions()

    def get_outputs(self):
        return self.global_control.get_model().get_outputs()

    def get_organs(self):
        # Return the list of organs in the model
        return self.global_control.get_model().get_organs()

    def get_organ_names(self):
        return self.global_control.get_model().get_organs().keys()

    def set_colors_for_global(self, name):
        self.current_global = name
        # If we select a global value to visualize, this function updates the nodes involved so we can see how far each
        # node is in their range with respect to this value
        color_scheme_names = self.global_control.get_model().color_schemes[name]

        gradient = self.context_pane.colorBar.getLookupTable(100) # A lookup table giving RGB colors

        for organ in self.global_control.get_model().organs.values():
            if organ.get_name() in color_scheme_names:
                # We get the reference range for this variable within this particular organ
                range = organ.get_local_ranges()[color_scheme_names[organ.get_name()]]
                # Using the range, and the gradient we previously obtained, we update the nodes with a color
                self.ui.scene.items[organ.get_name()].set_color(range, gradient)
            else:
                self.ui.scene.items[organ.get_name()].set_gray()
        self.ui.scene.update()

    def change_context_organ(self, organ):
        # Change the organ being displayed in the context menu on the right dock
        self.context_pane.change_context_organ(organ)

    def open_new_db(self):
        # This is called when the button to open a db is clicked in the menu
        if self.global_control.open_new_db():
            new_model = self.global_control.model_control.get_model()
            self.ui.scene.load_from_model(new_model)
            # After changing the model and the database inside the controller, we ask the UI to update itself
            self.ui.reload()

    def init_empty_model(self):
        new_model = self.global_control.model_control.get_model()
        self.ui.scene.load_from_model(new_model)
        self.ui.reload()

    def add_global_input(self, name, min, val, max):
        self.get_model().add_global_parameter(name, [min, max, val])

    def get_global_inputs(self):
        return self.get_model().get_global_param_ranges()

    def remove_global_input(self, input_name):
        self.get_model().remove_global_param(input_name)

    def organ_local_changed(self, name, label, new_value):
        # If the user changes a local value in an organ, this function is called. We change the local value and update
        # the UI accordingly
        organ = self.context_pane.current_organ
        organ.local_changed(name, new_value)
        label.setText(str(round(new_value,2)))
        self.context_pane.update_output(None, None)

    def add_global_function(self, f_name, f_str):
        self.global_control.get_model().add_global_func(f_name, f_str)

    def remove_global_func(self, removable_func):
        self.global_control.get_model().remove_global_func(removable_func)

    def get_global_functions(self):
        # Returns the global functions defined in the model
        return self.global_control.get_model().get_global_functions()

    def verify_function(self, func):
        # Verifies that the argument can be used as a global function
        return self.global_control.get_model().verify_function(func)

    def input_slider_changed(self, name, value):
        return self.global_control.get_model().param_changed(name, value)
