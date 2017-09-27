import os
from tinydb import TinyDB, Query

from function_list import create_functions


class Organ:
    """The class which represents all organs"""

    def __init__(self, name = "Default organ", category = "SystemicParameters"):
        self.name = name
        db_path = os.getcwd()
        self._database = TinyDB(db_path + '/db/organ_db.json')
        self._organ_parameters = self._database.table(category)
        organ = Query()
        initialization_values = self._organ_parameters.search(organ.name == name)
        self._function_vector = create_functions(initialization_values[0]['function_vector'])


    def __str__(self):
        return self.name

    def calculate(self, v_in: dict) -> dict:
        out = dict()
        for element in v_in:
            out[element] = self._function_vector[element](v_in[element])
        return out
