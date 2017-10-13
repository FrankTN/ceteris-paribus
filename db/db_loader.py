import os
from tinydb import TinyDB, Query
import ast2json

organ_db = TinyDB(os.getcwd() + "/organ_db.json")
organ_db.purge_table("SystemicParameters")
systemic_function_table = organ_db.table("SystemicParameters")
systemic_function_table.insert({"state": "rest", "name": "brain", "volume": 1.4, "BF": 1, "CMRO2": 3.7, "VO2": 51.8, "RQ": 1, "VCO2": 51.8})
systemic_function_table.insert({"state": "rest", "name": "heart", "volume": 0.35, "BF": 0.125, "CMRO2": 11, "VO2": 38.5, "RQ": 0.75, "VCO2": 28.875})
systemic_function_table.insert({"state": "rest", "name": "liver", "volume": 1.56, "BF": 1.5, "CMRO2": 2.2, "VO2": 34.32, "RQ": 0.8, "VCO2": 27.456})
systemic_function_table.insert({"state": "rest", "name": "gut", "volume": 1})
systemic_function_table.insert({"state": "rest", "name": "pancreas", "volume": 0.1})
systemic_function_table.insert({"state": "rest", "name": "kidneys", "volume": 0.26, "BF": 1, "CMRO2": 6.8, "VO2": 17.68, "RQ": 0.85, "VCO2": 15.028})
systemic_function_table.insert({"state": "rest", "name": "spleen", "volume": 0.14})
systemic_function_table.insert({"state": "rest", "name": "thyroid", "volume": 0.015})
systemic_function_table.insert({"state": "rest", "name": "muscles", "volume": 30, "BF": 0.5, "CMRO2": 0.18, "VO2": 54, "RQ": 0.85, "VCO2": 45.9})
systemic_function_table.insert({"state": "rest", "name": "diaphragm", "volume": 0.3})
systemic_function_table.insert({"state": "rest", "name": "adipose", "volume": 15})
systemic_function_table.insert({"state": "rest", "name": "skin", "volume": 10, "VO2": 38, "VCO2": 34.2})
systemic_function_table.insert({"state": "rest", "name": "blood", "volume": 5})
systemic_function_table.insert({"state": "rest", "name": "bones", "volume": 9})




organ_db.purge_table("PulmonaryParameters")
pulmonary_function_table = organ_db.table("PulmonaryParameters")

pulmonary_function_table.insert({"state": "rest", "name": "lung", "volume": 0.8, "VO2": -234.3, "VCO2": -203.259})

organ_db.purge_table("GlobalParameters")
global_param_table = organ_db.table("GlobalParameters")
global_param_table.insert({"name": "global_values", "input_vector_types":{"VO2": "abs","VCO2": "abs"}, "blood_vol": 5000})

# This is just used for testing
organ = Query()
result = pulmonary_function_table.search(organ.name == "lungs")
