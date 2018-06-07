"""This module contains the class for creating a new node. This dialog invokes the other sub-dialogs when required and
    orchestrates the entire process."""
from ceteris_paribus.gui.dialogs.function_dialog import FunctionDialog
from ceteris_paribus.gui.dialogs.name_dialog import NameDialog
from ceteris_paribus.gui.dialogs.source_dialog import SourceDialog
from ceteris_paribus.gui.dialogs.var_dialog import VarDialog


class NewNodeDialog(object):
    """ This class is used when creating new nodes"""

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.name = None
        self.sources = None
        self.functions = {}
        self.variables = {}

    def run(self):
        name_dialog = NameDialog()
        if name_dialog.exec_():
            # handle name
            self.name = name_dialog.name_field.text()
        else:
            # If we reject during naming return false
            return False
        source_dialog = SourceDialog(self.controller)
        if source_dialog.exec_():
            # handle source, which represents the organ we are receiving information from
            self.sources = source_dialog.get_source()
            for source in self.sources:
                # Retrieve the source organ, or the global input, according to the name of the source
                if source == "Global Input":
                    self.variables = {**self.variables, **self.controller.get_global_param_ranges()}
                else:
                    locals_of_source = self.controller.get_organs()[source].get_local_param_ranges()
                    # Unroll source locals into general variables
                    self.variables = {**self.variables, **locals_of_source}

                    funcs_of_source = self.controller.get_organs()[source].get_funcs()
                    # Unroll source functions into the functions defined here
                    self.functions = {**self.functions, **funcs_of_source}
        else:
            # If we reject during source selection return false
            return False
        var_dialog = VarDialog(self.variables)
        var_dialog.exec_()
        # self.variables has been updated, we can now write functions
        function_dialog = FunctionDialog(self.variables, self.name, self.functions)
        if function_dialog.exec_():
            # handle functions
            self.functions = function_dialog.get_functions()
        else:
            # If we reject during naming return false
            return False
        return True

    def get_variables(self):
        return self.variables

    def get_name(self):
        return self.name

    def get_funcs(self):
        return self.functions

    def get_sources(self):
        return self.sources
