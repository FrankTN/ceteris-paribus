import os
from tinydb import TinyDB, Query

from organ_functions import create_functions


class Organ(object):
    """The class which represents all organs"""

    def __init__(self, name = "Default organ", category = "SystemicParameters"):
        self.name = name
        db_path = os.getcwd()
        self._database = TinyDB(db_path + '/db/organ_db.json')
        self._organ_parameters = self._database.table(category)
        organ = Query()
        initialization_values = self._organ_parameters.search(organ.name == name)
        self._function_vector = create_functions(initialization_values[0]['function_vector'])

    def get_function_vector(self):
        return self._function_vector

    def __str__(self):
        return self.name

    def calculate(self, in_value, param_name: str) -> float:
        return self._function_vector[param_name](in_value)
