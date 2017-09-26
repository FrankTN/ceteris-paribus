import inspect
import os
from functools import partial

import function_list
from tinydb import TinyDB, Query

organ_db = TinyDB(os.getcwd() + "/organ_db.json")
organ_db.purge_table("OrganParameters")
organ_function_table = organ_db.table("OrganParameters")

organ_function_table.insert({"name": "lungs", "function_vector": {"VCO2": {"type": "linear", "coeffs": [1,200]},
                                                                  "VO2": {"type": "linear", "coeffs": [1,200]}}})
organ_function_table.insert({"name": "other", "function_vector": {"VCO2": {"type": "linear", "coeffs": [1,-200]},
                                                                  "VO2": {"type": "linear", "coeffs": [1,-200]}}})

organ = Query()
result = organ_function_table.search(organ.name == "lungs")
print(result[0])

a,b = result[0]['function_vector']['VO2']['coeffs']

r = partial(function_list.generic_linear_function, a, b)
function_list.parse_f_vector(result,'VO2')
print(r(4))
