""" This method fills out a new database from scratch. It is used for testing purposes"""

import os
from tinydb import TinyDB, Query

# TODO the fractions are still incorrect! There is a numerical error which will propagate.
organ_db = TinyDB(os.getcwd() + "/organ_db.json")
organ_db.purge_table("SystemicParameters")
systemic_function_table = organ_db.table("SystemicParameters")
systemic_function_table.insert({"state": "rest", "name": "brain", "Wfrac": 0.0175675676, "BF": 1, "CMRO2": 3.7, "VO2": 51.8, "RQ": 1, "VCO2": 51.8})
systemic_function_table.insert({"state": "rest", "name": "heart", "Wfrac": 0.00418918919, "BF": 0.125, "CMRO2": 11, "VO2": 38.5, "RQ": 0.75, "VCO2": 28.875})
systemic_function_table.insert({"state": "rest", "name": "liver", "Wfrac": 0.0189189189, "BF": 1.5, "CMRO2": 2.2, "VO2": 34.32, "RQ": 0.8, "VCO2": 27.456})
systemic_function_table.insert({"state": "rest", "name": "gut", "Wfrac": 0.0405405405})
systemic_function_table.insert({"state": "rest", "name": "pancreas", "Wfrac": 0.00135135135})
systemic_function_table.insert({"state": "rest", "name": "kidneys", "Wfrac": 0.00391891892, "BF": 1, "CMRO2": 6.8, "VO2": 17.68, "RQ": 0.85, "VCO2": 15.028})
systemic_function_table.insert({"state": "rest", "name": "spleen", "Wfrac": 0.00189189189})
systemic_function_table.insert({"state": "rest", "name": "thyroid", "Wfrac": 0.0002027027})
systemic_function_table.insert({"state": "rest", "name": "muscles", "Wfrac": 0.39729729729, "BF": 0.5, "CMRO2": 0.18, "VO2": 54, "RQ": 0.85, "VCO2": 45.9})
systemic_function_table.insert({"state": "rest", "name": "diaphragm", "Wfrac": 0.00405405405})
systemic_function_table.insert({"state": "rest", "name": "adipose", "Wfrac": 0.24324324324})
systemic_function_table.insert({"state": "rest", "name": "skin", "Wfrac": 0.0911486487, "VO2": 38, "VCO2": 34.2})
systemic_function_table.insert({"state": "rest", "name": "blood", "Wfrac": 0.06756756756})
systemic_function_table.insert({"state": "rest", "name": "bones", "Wfrac": 0.1081081081})




organ_db.purge_table("PulmonaryParameters")
pulmonary_function_table = organ_db.table("PulmonaryParameters")

pulmonary_function_table.insert({"state": "rest", "name": "lung", "Wfrac": 0.0108108108, "VO2": -234.3, "VCO2": -203.259})

organ_db.purge_table("GlobalParameters")
global_param_table = organ_db.table("GlobalParameters")
global_param_table.insert({"name": "global_values", "input_vector_types":{"VO2": "abs","VCO2": "abs"}, "blood_vol": 5000,
                              "glu_art_conc": 5, "lac_art_conc": 1, "ox_art_conc": 10, "co2_art_conc": 25, "ffa_art_conc": 1})

# This is just used for testing
organ = Query()
result = pulmonary_function_table.search(organ.name == "lungs")

total = 0
for organ in systemic_function_table.all():
    total += organ['Wfrac']
print(total)