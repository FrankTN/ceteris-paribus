import os
from tinydb import TinyDB, Query
import function_list

organ_db = TinyDB(os.getcwd() + "/organ_db.json")
organ_db.purge_table("SystemicParameters")
systemic_function_table = organ_db.table("SystemicParameters")
systemic_function_table.insert({"name": "other", "weight": "80", "frac": 1, "function_vector":
                                                                 {"VCO2": {"type": "linear", "coeffs": [1,-200]},
                                                                  "VO2": {"type": "linear", "coeffs": [1,-200]}}})

systemic_function_table.insert({"name": "heart", "weight": "0.3", "frac": 1, "function_vector":
                                                                 {"VCO2": {"type": "linear", "coeffs": [1,-30]},
                                                                  "VO2": {"type": "linear", "coeffs": [1,-30]}}})

organ_db.purge_table("PulmonaryParameters")
pulmonary_function_table = organ_db.table("PulmonaryParameters")

pulmonary_function_table.insert({"name": "lungs", "weight": "1.2", "frac": 1, "function_vector":
                                                                {"VCO2": {"type": "linear", "coeffs": [1,200]},
                                                                  "VO2": {"type": "linear", "coeffs": [1,200]}}})

organ_db.purge_table("GlobalParameters")
global_param_table = organ_db.table("GlobalParameters")
global_param_table.insert({"name": "global_values", "input_vector":["VO2","VCO2"]})

# This is just used for testing
organ = Query()
result = pulmonary_function_table.search(organ.name == "lungs")
print(result)
function_list.parse_f_vector(result[0]['function_vector']['VO2'])
