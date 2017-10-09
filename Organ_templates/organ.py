import os
from tinydb import TinyDB, Query

from organ_functions import create_functions


def load_from_db():
    pass


class Organ(object):
    """The class which represents all organs"""

    def __init__(self, organ_info: dict):
        for property in organ_info.keys():
            self.__setattr__(property, organ_info[property])

    def get_function_vector(self):
        return self._function_vector

    def __str__(self):
        return self.name

    def calculate(self, in_value, param_name: str) -> float:
        return self._function_vector[param_name](in_value)
