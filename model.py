from PyQt5.QtWidgets import QMessageBox

from db.function_parser import EvalWrapper
from organ_templates.organ import Organ


class Model(object):
    """ This class represents the model in the Model-View-Controller architecture.
        It contains two lists of organs representing the systemic and pulmonary circulation.
        To initialize, a JSON-database is loaded using the TinyDB framework.
    """
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        # Since we only create a model after we know that the db has been loaded, we know that getdb() works
        self._database = self.controller.get_db()
        self.initialize_globals()
        self.initialize_organs()

    def initialize_globals(self):
        # From the database, get the input parameters.
        self._params = {}
        for param in self._database.table("GlobalParameters").all():
            self._params.update(param)
        self._constants = {}
        for const in self._database.table("GlobalConstants").all():
            self._constants.update(const)

        self._global_funcs = {}
        for func in self._database.table("GlobalFunctions").all():
            self._global_funcs.update(func)

        self._globals = {**self._params, **self._constants}

    def initialize_organs(self):
        """ Using the database, this function reads the values for all the organs.
            Currently, the lungs are created, and an other compartment is added to
            simulate the systemic circulation in its entirety.
        """
        self.organs = {}
        for organ_info in self._database.table("SystemicOrgans").all():
            # Params in this object are defined as a list, where the first two values are the range and the third value
            # is its current value. An organ is not concerned with the allowed range of the params, and thus only
            # receives this value.
            rangeless_params = {}
            for parameter in self._params:
                rangeless_params[parameter] = self._params[parameter][2]
            self.organs[organ_info['name']] = Organ(organ_info, rangeless_params, self._constants)

    def param_changed(self, name: str, slider):
        new_value = slider.value()
        self._params[name][2] = new_value
        rangeless_params = {}
        for parameter in self._params:
            rangeless_params[parameter] = self._params[parameter][2]

        for organ in self.organs.values():
            organ.set_globals({**rangeless_params, **self._constants})
        print(name + ": " + str(new_value))

    def close(self):
        self._database.close()

    def get_global_values(self):
        return self._globals

    def get_params(self):
        return self._params

    def get_constants(self):
        return self._constants

    def update_model(self, objectName: str, value):
        self.__setattr__(objectName, value)

    def get_outputs(self):
        # Make a shallow copy of the global function dict, so that we can freely modify it
        unresolved_global_funcs = self._global_funcs.copy()
        changed = True
        output = {}
        while changed:
            changed = False
            for function_name in list(unresolved_global_funcs):
                evaluator = EvalWrapper(self.organs)
                evaluator.set_function(unresolved_global_funcs[function_name])
                result = evaluator.evaluate()
                if result is not None:
                    changed = True
                    output[function_name] = result
                    unresolved_global_funcs.pop(function_name)
            return output
        # if unresolved_global_funcs:
        #     msg = QMessageBox()
        #     msg.setWindowTitle("Error")
        #     unresolved_string = {str(x) + ": " + unresolved_funcs[x] + "\n" for x in unresolved_funcs.keys()}
        #     msg.setText(
        #         "The specified database cannot create the organ " + self.get_name() + ",\nplease look at the following unresolvable functions: \n" + "".join(
        #             unresolved_string))
        #     msg.exec_()
        #     quit(-1)
