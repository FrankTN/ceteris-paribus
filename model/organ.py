from PyQt5.QtWidgets import QDialog, QErrorMessage, QMessageBox

from ceteris_paribus.db.function_parser import EvalWrapper, Transformer, evaluate_functions


class Organ(object):
    """The class which represents all organs"""

    def __init__(self, organ_info, input_params, input_constants, pos):
        """ This generic implementation of an organ in the model uses the __setattr__ method to add attributes.
            Adding attributes in this way is necessary since not all attributes are defined for each organ.
        """
        self.input_params = input_params
        self.input_constants = input_constants
        self.pos = pos
        if organ_info:
            for property in organ_info.keys():
                self.__setattr__(property, organ_info[property])

        # The defined variables dict is a combination of all the variables and their values available to this organ
        # It will be used by the evaluator to resolve all functions and their values
        self.defined_variables = {**self.get_local_vals(), **self.input_params, **self.input_constants}

        self.results = {}
        self.evaluate()

    def set_globals(self, new_globals):
        """
        This functions swaps the global variables of the organ. As a side-effect, the defined_variables are also changed
        :param new_globals: a dict containing the new global variables
        :return: None
        """
        self.input_params = new_globals
        self.defined_variables = {**self.defined_variables, **self.input_params, **self.input_constants}


    def evaluate(self):
        unresolved_funcs = getattr(self, 'functions').copy()
        self.defined_variables = {**self.defined_variables, **evaluate_functions(unresolved_funcs, self.defined_variables)}

    def get_name(self):
        return getattr(self, 'name', 'default_organ')

    def set_name(self, name):
        setattr(self, 'name', name)

    def local_changed(self, name: str, new_value):
        # Set local value to the new one
        self.defined_variables[name] = new_value
        self.get_local_ranges()[name][2] = new_value

    def get_pos(self):
        return self.pos

    def get_defined_variables(self) -> dict:
        # Returns all variables defined for this organ and their values in a single dict
        self.evaluate()
        self.defined_variables.pop('__builtins__', None)
        return self.defined_variables

    def get_inputs(self) -> dict:
        # Returns the global values as known to this organ in a single dict
        return self.input_params

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
