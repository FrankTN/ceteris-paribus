from PyQt5.QtWidgets import QDialog, QErrorMessage, QMessageBox

from ceteris_paribus.db.function_parser import EvalWrapper, Transformer


class Organ(object):
    """The class which represents all organs"""

    def __init__(self, organ_info: dict, global_params: dict, global_constants: dict, pos):
        """ This generic implementation of an organ in the model uses the __setattr__ method to add attributes.
            Adding attributes in this way is necessary since not all attributes are defined for each organ.
        """
        self.global_params = global_params
        self.global_constants = global_constants
        self.pos = pos
        if organ_info:
            for property in organ_info.keys():
                self.__setattr__(property, organ_info[property])

        # The defined variables dict is a combination of all the variables and their values available to this organ
        # It will be used by the evaluator to resolve all functions and their values
        self.defined_variables = {**self.get_local_vals(), **self.global_params, **self.global_constants}

        self.results = {}
        self.evaluate()

    def set_globals(self, new_globals: dict):
        """
        This functions swaps the global variables of the organ. As a side-effect, the defined_variables are also changed
        :param new_globals: a dict containing the new global variables
        :return: None
        """
        self.global_params = new_globals
        self.get_defined_variables()

    def evaluate(self):
        """
        Evaluate all functions defined for the organ. This function naively keeps trying to solve for all variables
        until no new changes occur. If all variables have been resolved execution was successful, otherwise we display
        an error message.
        :return: None
        """
        #TODO combine this function with the one in the global model
        unresolved_funcs = getattr(self, 'functions').copy()
        changed = True
        while changed:
            changed = False
            for function_name in list(unresolved_funcs):
                evaluator = EvalWrapper(self.defined_variables, Transformer())
                evaluator.set_function(unresolved_funcs[function_name])
                result = evaluator.evaluate()
                if result is not None:
                    changed = True
                    self.defined_variables[function_name] = result
                    unresolved_funcs.pop(function_name)
        if unresolved_funcs:
            msg = QMessageBox()
            msg.setWindowTitle("Error")
            unresolved_string = {str(x) + ": " + unresolved_funcs[x] + "\n" for x in unresolved_funcs.keys()}
            msg.setText("The specified database cannot create the organ " + self.get_name() + ",\nplease look at the following unresolvable functions: \n" + "".join(unresolved_string))
            msg.exec_()
            quit(-1)

    def get_name(self):
        return getattr(self, 'name', 'default_organ')

    def local_changed(self, name: str, slider):
        # Get new value from the slider
        new_value = slider.value()
        # Set local value to the new one
        self.get_local_ranges()[name][2] = new_value

    def get_pos(self):
        return self.pos

    def get_defined_variables(self) -> dict:
        # Returns all variables defined for this organ and their values in a single dict
        self.defined_variables = {**self.get_local_vals(), **self.global_params, **self.global_constants}
        self.defined_variables.pop('__builtins__', None)
        return self.defined_variables

    def get_globals(self) -> dict:
        # Returns the global values as known to this organ in a single dict
        return self.global_params

    def get_local_ranges(self) -> dict:
        # Returns only the locally defined variables
        local_ranges = getattr(self, 'variables')
        local_ranges.pop('__builtins__', None)
        return getattr(self, 'variables')

    def get_local_vals(self) -> dict:
        # returns only the third value in the list
        local_vals = {}
        ranged_vals = getattr(self, 'variables')
        ranged_vals.pop('__builtins__', None)
        for param in ranged_vals:
            local_vals[param] = ranged_vals[param][2]
        return local_vals

    def get_funcs(self) -> dict:
        # Returns the local functions defined for this organ
        return getattr(self, 'functions')

    def __str__(self) -> str:
        return str(getattr(self, 'name', 'default_organ')) + ":\n\tFunctions: " + str(
            getattr(self, 'functions')) + "\n\t\tVars: " + str(getattr(self, 'variables'))
