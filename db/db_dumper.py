""" This module contains functions for serializing the data in the program to a database.
"""

import os

from tinydb import TinyDB

import organ_functions


def dump_model(model, db_name: str = "organ_db.json"):
    """Serialize a model as a JSON file in such a way that it can be reopened at any moment for later use."""
    #TODO remove duplicate code.
    target_db = TinyDB(os.getcwd() + "/db/" + db_name)
    global_params = target_db.table("GlobalParameters")
    global_params.insert(model.get_global())

    systemic_params = target_db.table("SystemicParameters")
    systemic_vals = model.get_systemic()

    for vertex in systemic_vals[0].vertices():
        name = vertex.name
        frac = systemic_vals[1][name]
        f_vec = vertex.get_function_vector()
        f_dict = {}
        for func in f_vec:
            coeffs = list(f_vec[func].args)
            type = organ_functions.parse_type(f_vec[func])
            inner_dict = {}
            inner_dict["coeffs"] = coeffs
            inner_dict["type"] = type
            f_dict[func] = inner_dict
        systemic_params.insert({"name": name, "frac": frac, "function_vector": f_dict})

    pulmonary_params = target_db.table("PulmonaryParameters")
    pulmonary_vals = model.get_pulmonary()
    for vertex in pulmonary_vals[0].vertices():
        name = vertex.name
        frac = pulmonary_vals[1][name]
        f_vec = vertex.get_function_vector()
        f_dict = {}
        for func in f_vec:
            coeffs = list(f_vec[func].args)
            type = organ_functions.parse_type(f_vec[func])
            inner_dict = {}
            inner_dict["coeffs"] = coeffs
            inner_dict["type"] = type
            f_dict[func] = inner_dict
        pulmonary_params.insert({"name": name, "frac": frac, "function_vector": f_dict})
