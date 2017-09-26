import os
from tinydb import TinyDB, Query


class Organ:
    """The class which represents all organs"""

    def __init__(self, name = "Default organ"):
        self._name = name
        db_path = os.path.abspath('..')
        self._database = TinyDB(db_path + '/db/organ_db.json')
        self._organ_parameters = self._database.table("OrganParameters")
        organ_parameters = Query()
        self._function_vector = self._database.search(organ_parameters.name == name)

    def __str__(self):
        return self._name

    def calculate(self, v_in: dict) -> dict:
        out = dict()
        for element in zip(v_in, self._function_vector):
            val, func = element
            out[val] = func(v_in[val])
        return out
