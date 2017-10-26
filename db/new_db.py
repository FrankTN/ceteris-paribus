
import os
from tinydb import TinyDB, Query

from organ_templates.organ import Organ

organ_db = TinyDB(os.getcwd() + "/new_organ_db.json")

organ_db.purge_table("GlobalParameters")
global_param_table = organ_db.table("GlobalParameters")
global_param_table.insert({"BodyCO": [0, 10000, 5000]})
global_param_table.insert({"BodyVO2": [0, 400, 250]})

organ_db.purge_table("GlobalConstants")
global_constant_table = organ_db.table("GlobalConstants")
global_constant_table.insert({"mol_to_ml_37_deg" : 25.48657718})
global_constant_table.insert({"SMR_glu_lung" : 0.4})
global_constant_table.insert({"glu_art" : 5.0})
global_constant_table.insert({"lac_art" : 1.0})
global_constant_table.insert({"O2_art" : 10.0})
global_constant_table.insert({"CO2_art" : 25.0})
global_constant_table.insert({"FFA_art" : 0.0})


# definitions of all the functions
f_global_VO2 = "sum(VO2)"
f_global_VCO2 = "sum(VCO2)"
f_global_RQ = "avg(RQ)"
f_global_sVO2 = "sum(VO2) / BW"
f_global_sVCO2 = "sum(VCO2) / BW"
f_art_PO2 = "udef"
f_art_sO2 = "udef"
f_art_PCO2 = "udef"



f_VO2 = "mol_to_ml_37_deg * SMRO2 * Organ_Weight"
f_VCO2 = "mol_to_ml_37_deg * SMRCO2 * Organ_Weight"
f_SMRCO2 = "RQ * SMRO2"
f_SMRglu_ox = "WQ * SMRglu"
f_SMRlac = "2 * WQ * SMRglu"
f_SMRFFA = "6 * (1 - RQ)/(27*rq - 18) * SMRglu_ox"
f_ven_glu = "glu_art - Organ_Weight * (SMRglu - SMRglu_prod) / BF"
f_ven_O2 = "O2_art - Organ_Weight * SMRO2 / BF"
f_ven_CO2 = "CO2_art + Organ_Weight * SMRCO2 / BF"
f_ven_lac = "lac_art + Organ_Weight * (SMRglu - SMRglu_prod) / BF"


organ_db.purge_table("SystemicOrgans")
systemic_organ_table = organ_db.table("SystemicOrgans")
systemic_organ_table.insert({"name" : "Skeletal muscle", "functions": {"calcVO2": f_VO2}, "vars" : {"BF": 0.6, "SMRO2": 0.18, "Organ_Weight" : 27, "VO2": 48.6, "RQ": 0.85, "VCO2": 41.31}, "pos": [200,200]})
systemic_organ_table.insert({"name" : "Adipose tissue", "functions": {"calcVO2": "mol_to_ml_37_deg * SMRO2 * Organ_Weight"}, "vars" : {"BF": 0.2, "SMRO2": 0.07, "Organ_Weight" : 18, "VO2": 12.6}, "pos": [200,300]})
systemic_organ_table.insert({"name" : "Skin", "functions": {"calcVO2" : "mol_to_ml_37_deg * SMRO2 * Organ_Weight"}, "vars" : {"BF": 0.5, "SMRO2": 0.3, "Organ_Weight" : 10, "VO2": 30, "RQ": 0.9, "VCO2": 27}, "pos": [200,100]})
systemic_organ_table.insert({"name" : "Bones", "functions": {"calcVO2" : "mol_to_ml_37_deg * SMRO2 * Organ_Weight"}, "vars" : {"BF": 0.1, "SMRO2": 0.02, "Organ_Weight" : 8, "VO2": 1.6}, "pos": [200,0]})
systemic_organ_table.insert({"name" : "Blood", "functions": {"calcVO2" : "mol_to_ml_37_deg * SMRO2 * Organ_Weight"}, "vars" : {"BF": 0, "SMRO2": 0, "Organ_Weight" : 5, "VO2": 0, "WQ": 1}, "pos": [200,-100]})
systemic_organ_table.insert({"name" : "Gut", "functions": {"calcVO2" : "mol_to_ml_37_deg * SMRO2 * Organ_Weight"}, "vars" : {"SMRO2": 0.1, "Organ_Weight" : 5, "VO2": 3}, "pos": [200,-200]})
systemic_organ_table.insert({"name" : "Liver", "functions": {"calcVO2" : "mol_to_ml_37_deg * SMRO2 * Organ_Weight"}, "vars" : {"BF": 1.5, "SMRO2": 2.2, "Organ_Weight" : 1.4, "VO2": 30.8, "RQ": 0.8, "VCO2": 24.64}, "pos": [200,-300]})
systemic_organ_table.insert({"name" : "Brain", "functions": {"calcVO2" : "mol_to_ml_37_deg * SMRO2 * Organ_Weight"}, "vars" : {"BF": 1, "SMRO2": 3.7, "Organ_Weight" : 1.3, "VO2": 48.1, "RQ": 1, "WQ": 0, "VCO2": 48.1}, "pos": [200,300]})
systemic_organ_table.insert({"name" : "Heart", "functions": {"calcVO2" : "mol_to_ml_37_deg * SMRO2 * Organ_Weight"}, "vars" : {"BF": 0.125, "SMRO2": 11, "Organ_Weight" : 0.31, "VO2": 34.1, "RQ": 0.75, "WQ": 0, "VCO2": 25.575}, "pos": [200,-400]})
systemic_organ_table.insert({"name" : "Diaphragm", "functions": {"calcVO2" : "mol_to_ml_37_deg * SMRO2 * Organ_Weight"}, "vars" : {"BF": 0.01, "SMRO2": 1, "Organ_Weight" : 0.31, "VO2": 3}, "pos": [200,400]})
systemic_organ_table.insert({"name" : "Kidneys", "functions": {"calcVO2" : "mol_to_ml_37_deg * SMRO2 * Organ_Weight"}, "vars" : {"BF": 1, "SMRO2": 6.8, "Organ_Weight" : 0.29, "VO2": 19.72, "RQ": 0.85, "VCO2": 16.762}, "pos": [200,-500]})
systemic_organ_table.insert({"name" : "Spleen", "functions": {}, "vars" : {"Organ_Weight" : 0.14}, "pos": [200,500]})
systemic_organ_table.insert({"name" : "Pancreas", "functions": {}, "vars" : {"Organ_Weight" : 0.1}, "pos": [200,-600]})
systemic_organ_table.insert({"name" : "Thyroid", "functions": {}, "vars" : {"BF": 0.001, "Organ_Weight" : 0.015}, "pos": [200,-600]})

#organ = Organ(systemic_organ_table.all()[0], global_param_table.all(), global_constant_table.all())