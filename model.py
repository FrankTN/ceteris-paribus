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

        self._globals = {**self._params, **self._constants}

    def initialize_organs(self):
        """ Using the database, this function reads the values for all the organs.
            Currently, the lungs are created, and an other compartment is added to
            simulate the systemic circulation in its entirety.
        """
        self.organs = []
        for organ_info in self._database.table("SystemicOrgans").all():
            # Params in this object are defined as a list, where the first two values are the range and the third value
            # is its current value. An organ is not concerned with the allowed range of the params, and thus only
            # receives this value.
            rangeless_params = {}
            for parameter in self._params:
                rangeless_params[parameter] = self._params[parameter][2]
            self.organs.append(Organ(organ_info, rangeless_params, self._constants))

    def global_changed(self):
        for organ in self.organs:
            organ.set_globals(self._globals)

    def param_changed(self, name: str, new_value):
        self._params[name][2] = new_value
        self.calculate()
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

    def calculate(self):
        self.calculate_organ_values()
        self.calculate_global_values()

    def calculate_global_values(self):
        pass

    def calculate_organ_values(self):
        pass
