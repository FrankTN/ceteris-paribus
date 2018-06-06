from PyQt5.QtWidgets import QMessageBox

from ceteris_paribus.db.function_parser import EvalWrapper, ModelTransformer, evaluate_functions
from ceteris_paribus.model.organ import Organ


class GlobalModel(object):
    """ This class represents the model in the Model-View-Controller architecture.
        To initialize, a JSON-database is loaded using the TinyDB framework.
    """

    def __init__(self, controller):
        super().__init__()
        self.organs = {}
        self._global_funcs = {}
        self._global_constants = {}
        self._global_params = {}
        self.color_schemes = {}
        self.controller = controller
        # Since we only create a model after we know that the db has been loaded, we know that get_db() works
        if self.controller.get_db() is not None:
            self._database = self.controller.get_db()
            self.initialize_globals()
            self.initialize_organs()
        self.vars = {}

    def initialize_globals(self):
        """ This function retrieves all globally defined values from the database."""
        # From the database, get the global input parameters.
        global_param_table = self._database.table("GlobalParameters").all()
        for param in global_param_table:
            self._global_params.update(param)
        # The globally defined constants are also retrieved from the database
        global_const_table = self._database.table("GlobalConstants").all()
        for const in global_const_table:
            self._global_constants.update(const)
        # Finally, the global functions are retrieved
        global_func_table = self._database.table("GlobalFunctions").all()
        for func in global_func_table:
            self._global_funcs.update(func)
        # _globals is defined as the dictionary containing all globally accessible values, constant or variable
        self._globals = {**self._global_params, **self._global_constants}

    def initialize_organs(self):
        """ Using the database, this function creates all the organs and adds them to the list of organs maintained by
            the model."""
        pos = [0, 0]
        self.count = 0
        rangeless_globals = self.make_rangeless_params(self._global_params)
        for organ_info in self._database.table("SystemicOrgans").all():
            # In the default UI we stack the organs on top of each other by generating a pos for each
            if self.count % 2 == 0:
                pos[1] *= -1
            else:
                pos[1] *= -1
                pos[1] += 35
            # An organ_info key gives us access to all the information required to instantiate a single organ.
            self.organs[organ_info['name']] = Organ(organ_info, rangeless_globals, self._global_constants, pos[:])
            self.count += 1

    def make_rangeless_params(self, params_with_range):
        """ This function removes redundant information from the global values"""
        rangeless_params = {}
        for parameter in params_with_range:
            # The global parameters are defined as a list, where the first two values are the range and the third
            # is its current value. An organ is not concerned with the allowed range of the params, and thus only
            # receives the third value.
            rangeless_params[parameter] = params_with_range[parameter][2]
        return rangeless_params

    def param_changed(self, name, new_value):
        """This function handles the updating of a parameter in response to the user interacting with the UI"""
        # Set the new value in the global params
        self._global_params[name][2] = new_value
        rangeless_params = self.make_rangeless_params(self._global_params)
        # We update each organ by explicitly resetting its globals
        for organ in self.organs:
            if organ != '__builtins__':
                self.organs[organ].set_globals({**rangeless_params, **self._global_constants})

    def get_all_variables(self):
        return self._globals

    def get_global_param_values(self):
        return {k: v[2] for k, v in self._global_params.items()}

    def get_global_param_ranges(self):
        return self._global_params

    def remove_global_param(self, name):
        del self._global_params[name]

    def get_global_constants(self):
        return self._global_constants

    def add_global_constant(self, name, val):
        if name in self._global_constants:
            msg = QMessageBox()
            msg.setWindowTitle("Warning")
            msg.setText(
                "The global constant you want to add already exists:\n" + name + " : " +
                str(self._global_constants[name]) + "\nOverwrite?")
            msg.setStandardButtons(QMessageBox.Yes)
            msg.addButton(QMessageBox.No)
            msg.setDefaultButton(QMessageBox.No)
            if msg.exec() == QMessageBox.Yes:
                self._global_constants[name] = val
        else:
            self._global_constants[name] = val

    def add_global_parameter(self, name, val):
        assert (len(val) == 3)
        if name in self._global_params:
            msg = QMessageBox()
            msg.setWindowTitle("Warning")
            msg.setText(
                "The global constant you want to add already exists:\n" + name + " : " +
                str(self._global_params[name]) + "\nOverwrite?")
            msg.setStandardButtons(QMessageBox.Yes)
            msg.addButton(QMessageBox.No)
            msg.setDefaultButton(QMessageBox.No)
            if msg.exec() == QMessageBox.Yes:
                self._global_params[name] = val
        else:
            self._global_params[name] = val

    def get_organs(self):
        return self.organs

    def get_global_functions(self):
        return self._global_funcs

    def remove_global_func(self, f_name):
        if f_name not in self._global_funcs:
            msg = QMessageBox()
            msg.setText("Unable to remove global function " + f_name)
            msg.exec()
            return
        self._global_funcs.pop(f_name, None)

    def add_global_func(self, f_name, f_string):
        if f_name in self._global_funcs:
            msg = QMessageBox()
            msg.setWindowTitle("Warning")
            msg.setText(
                "The global function you want to add already exists:\n" + f_name + " : " +
                str(self._global_funcs[f_name]) + "\nOverwrite?")
            msg.setStandardButtons(QMessageBox.Yes)
            msg.addButton(QMessageBox.No)
            msg.setDefaultButton(QMessageBox.No)
            if msg.exec() == QMessageBox.No:
                return
        if self.verify_function(f_string):
            self._global_funcs[f_name] = f_string
            print('The function was added')
        else:
            msg = QMessageBox()
            msg.setWindowTitle("Warning")
            msg.setText(
                "Adding the specified function invalidates the model, please ensure that the variables are defined"
                " first:\n " + f_name + " : " + f_string)
            msg.exec()

    def verify_function(self, function):
        # This function merely verifies whether a given function can be executed under the current model
        self.vars = {**self.vars, **self.organs}

        evaluator = EvalWrapper(self.vars, ModelTransformer(self.vars))
        evaluator.set_function(function)
        # The result of the evaluation is stored in the result variable if it exists
        result = evaluator.evaluate()
        if result is not None:
            # We obtained a result, therefore the evaluation works
            return True
        # The evaluation was not successful, as we did not obtain a result
        return False

    def get_outputs(self):
        """
        This function calculates the global outputs of the model
        :return: a dictionary containing the names of the outputs and their calculated values.
        """
        # Make a shallow copy of the global function dict, so that we can freely modify it
        copied_functions = self._global_funcs.copy()
        variables = {**self.vars, **self.organs}
        result = evaluate_functions(copied_functions, variables, self.color_schemes)
        return result

    def remove(self, organ):
        self.organs.pop(organ.get_name())

    def add(self, organ_info, pos):
        organ = Organ(organ_info, self.get_global_param_values(), self.get_global_constants(), pos)
        self.organs[organ.get_name()] = organ
        return organ
