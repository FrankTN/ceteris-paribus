from PyQt5.QtWidgets import QUndoStack

from ceteris_paribus.model.global_model import GlobalModel


class ModelController(object):
    """ The ViewController is a class in the controller module, it contains those functions concerned with controlling
        the UI. It is replaced when a different model is loaded"""

    def __init__(self, model_data):
        self.db = model_data
        # Create a global model instance
        self.model = GlobalModel(self)

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

    def param_changed(self, name, slider):
        # Another relay method to ensure the model is only used by the controller
        self.model.param_changed(name, slider)
