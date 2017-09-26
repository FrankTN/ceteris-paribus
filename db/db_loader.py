import inspect
import os
from functools import partial

import function_list
from tinydb import TinyDB, Query

organ_db = TinyDB(os.getcwd() + "/organ_db.json")
organ_db.purge_table("OrganParameters")
organ_function_table = organ_db.table("OrganParameters")
organ_function_table.insert({"name": "lungs", "frac": 1, "function_vector":
                                                                {"VCO2": {"type": "linear", "coeffs": [1,200]},
                                                                  "VO2": {"type": "linear", "coeffs": [1,200]}}})
organ_function_table.insert({"name": "other", "frac": 1, "function_vector":
                                                                 {"VCO2": {"type": "linear", "coeffs": [1,-200]},
                                                                  "VO2": {"type": "linear", "coeffs": [1,-200]}}})

organ_db.purge_table("GlobalParameters")
global_param_table = organ_db.table("GlobalParameters")
global_param_table.insert({"name": "global_values", "input_vector":["VO2","VCO2"]})

# This is just used for testing
organ = Query()
result = organ_function_table.search(organ.name == "lungs")
print(result[0])

a,b = result[0]['function_vector']['VO2']['coeffs']

r = partial(function_list.generic_linear_function, a, b)
function_list.parse_f_vector(result,'VO2')
print(r(4))
