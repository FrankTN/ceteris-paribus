from PyQt5.QtWidgets import QDialog, QErrorMessage, QMessageBox

from db.function_parser import EvalWrapper


class Organ(object):
    """The class which represents all organs"""

    def __init__(self, organ_info: dict, global_params: dict, global_constants: dict):
        """ This generic implementation of an organ in the model uses the __setattr__ method to add attributes.
            Adding attributes in this way is necessary since not all attributes are defined for each organ.
        """
        self.global_params = global_params
        self.global_constants = global_constants
        if organ_info:
            for property in organ_info.keys():
                self.__setattr__(property, organ_info[property])

        self.defined_variables = {**getattr(self,'vars'), **self.global_params, **self.global_constants}
        self.results = {}
        self.evaluate()

    def set_globals(self, new_globals):
        self.global_params = new_globals
        self.defined_variables = {**getattr(self,'vars'), **self.global_params, **self.global_constants}

    def evaluate(self):
        """
        Evaluate all functions defined for the organ.
        :return:
        """
        unresolved_funcs = getattr(self, 'functions').copy()
        changed = 1
        while changed:
            changed = 0
            for function_name in list(unresolved_funcs):
                evaluator = EvalWrapper(self.defined_variables)
                evaluator.set_function(unresolved_funcs[function_name])
                result = evaluator.evaluate()
                if result is not None:
                    changed = 1
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

    def get_vars(self):
        # Returns all variables defined for this organ and their values in a single dict
        return self.defined_variables

    def get_globals(self):
        return self.global_params

    def get_locals(self):
        return getattr(self, 'vars')

    def get_funcs(self):
        return getattr(self, 'functions')

    def __str__(self):
        return str(getattr(self, 'name', 'default_organ')) + ":\n\tFunctions: " + str(
            getattr(self, 'functions')) + "\n\t\tVars: " + str(getattr(self, 'vars'))
