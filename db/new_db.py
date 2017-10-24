
import os
from tinydb import TinyDB, Query

from organ_templates.organ import Organ

organ_db = TinyDB(os.getcwd() + "/new_organ_db.json")

organ_db.purge_table("GlobalParameters")
global_param_table = organ_db.table("GlobalParameters")
global_param_table.insert({"BF": [0, 10000, 5000]})
global_param_table.insert({"VO2": [0, 400, 250]})

organ_db.purge_table("GlobalConstants")
global_constant_table = organ_db.table("GlobalConstants")
global_constant_table.insert({"mol_to_ml_37_deg" : 25.48657718})
global_constant_table.insert({"SMR_glu_lung" : 0.4})

organ_db.purge_table("SystemicOrgans")
systemic_organ_table = organ_db.table("SystemicOrgans")

systemic_organ_table.insert({"name" : "Skeletal muscle", "functions": {"calcVO2" : "mol_to_ml_37_deg * SMRO2 * Organ_Weight"}, "vars" : {"SMRO2" : 0.18, "Organ_Weight" : 27}, "pos": [200,200]})
systemic_organ_table.insert({"name" : "Brain", "functions": {"calcVO2" : "mol_to_ml_37_deg * SMRO2 * Organ_Weight"}, "vars" : {"SMRO2" : 0.18, "Organ_Weight" : 27}, "pos": [200, 400]})

organ = Organ(systemic_organ_table.all()[0], global_param_table.all(), global_constant_table.all())