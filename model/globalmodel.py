from PyQt5.QtWidgets import QMessageBox

from db.function_parser import EvalWrapper, ModelTransformer
from model.organ import Organ


class GlobalModel(object):
    """ This class represents the model in the Model-View-Controller architecture.
        To initialize, a JSON-database is loaded using the TinyDB framework.
    """
    def __init__(self, controller):
        super().__init__()
        self.color_schemes = {}
        self.controller = controller
        # Since we only create a model after we know that the db has been loaded, we know that get_db() works
        self._database = self.controller.get_db()
        self.initialize_globals()
        self.initialize_organs()
        self.vars = {}

    def initialize_globals(self):
        """ This function retrieves all globally defined values from the database."""
        # From the database, get the global input parameters.
        self._global_params = {}
        for param in self._database.table("GlobalParameters").all():
            self._global_params.update(param)
        # The globally defined constants are also retrieved from the database
        self._global_constants = {}
        for const in self._database.table("GlobalConstants").all():
            self._global_constants.update(const)
        # Finally, the global functions are retrieved
        self._global_funcs = {}
        for func in self._database.table("GlobalFunctions").all():
            self._global_funcs.update(func)
        # _globals is defined as the dictionary containing all globally accessible values, constant or variable
        self._globals = {**self._global_params, **self._global_constants}

    def initialize_organs(self):
        """ Using the database, this function creates all the organs and adds them to the list of organs maintained by
            the model."""
        self.organs = {}
        pos = [0, 0]
        self.count = 0
        rangeless_globals = self.make_rangeless_params(self._global_params)
        for organ_info in self._database.table("SystemicOrgans").all():
            # organ_info['variables'] = self.make_rangeless_params(organ_info['variables'])
            # In the default UI we stack the organs on top of eachother by generating a pos for each
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

    def param_changed(self, name: str, slider):
        """This function handles the updating of a parameter in response to the user interacting with the UI"""
        new_value = slider.value()
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
        return {k : v[2] for k,v in self._global_params.items()}

    def get_global_param_ranges(self):
        return self._global_params

    def get_global_constants(self):
        return self._global_constants

    def get_organs(self):
        return self.organs

    def get_functions(self):
        return self._global_funcs

    def get_outputs(self):
        """
        This function calculates the global outputs of the model
        :return: a dictionary containing the names of the outputs and their calculated values.
        """
        # Make a shallow copy of the global function dict, so that we can freely modify it
        unresolved_global_funcs = self._global_funcs.copy()
        changed = True
        output = {}

        while changed:
            changed = False
            for function_name in list(unresolved_global_funcs):
                # For every unresolved functions, we create an evaluator object
                self.vars = {**self.vars, **self.organs}

                evaluator = EvalWrapper(self.vars, ModelTransformer())
                evaluator.set_function(unresolved_global_funcs[function_name])
                # The result of the evaluation is stored in the result variable if it exists
                result = evaluator.evaluate()
                required_vals = evaluator.transformer.visited
                self.color_schemes[function_name] = required_vals
                if result is not None:
                    # We have found a new result, therefore, we set changed to True and we store the result
                    changed = True
                    self.vars[function_name] = result
                    output[function_name] = result
                    # Finally, we remove the function we just resolved from the globals so that we don't loop infinitely
                    unresolved_global_funcs.pop(function_name)
        if unresolved_global_funcs:
            msg = QMessageBox()
            msg.setWindowTitle("Error")
            unresolved_string = {str(x) + ": " + unresolved_global_funcs[x] + "\n" for x in unresolved_global_funcs.keys()}
            msg.setText(
                "The specified database cannot create the model,\nplease look at the following unresolvable functions: \n" + "".join(
                    unresolved_string))
            msg.exec_()
            quit(-1)
        return output

    def remove(self, organ):
        self.organs.pop(organ.get_name())

    def add(self, organ_info, pos):
        organ = Organ(organ_info, self.get_global_param_values(), self.get_global_constants(), pos)
        self.organs[organ.get_name()] = organ
        return organ

