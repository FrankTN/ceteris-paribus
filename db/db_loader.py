
import os
from tinydb import TinyDB, Query

from ceteris_paribus.model.organ import Organ

organ_db = TinyDB(os.getcwd() + "/new_organ_db.json")

organ_db.purge_table("GlobalParameters")
global_param_table = organ_db.table("GlobalParameters")
global_param_table.insert({"BodyCO": [0, 10000, 5000]})
global_param_table.insert({"BodyVO2": [0, 400, 250]})
global_param_table.insert({"glu_art": [3.0, 7.0, 5.0]})
global_param_table.insert({"lac_art": [0.6, 1.8, 1.0]})
global_param_table.insert({"O2_art": [6, 30.0, 10.0]}) # Not based on anything, unable to find references
global_param_table.insert({"CO2_art": [6, 40.0, 25.0]}) # Not based on anything, unable to find references
global_param_table.insert({"FFA_art": [0, 0.0, 0.0]}) # Not based on anything, unable to find references
# TODO Hb
# TODO arterial pH


organ_db.purge_table("GlobalConstants")
global_constant_table = organ_db.table("GlobalConstants")
global_constant_table.insert({"mol_to_ml_37_deg" : 25.48657718})
global_constant_table.insert({"SMRglu_lung" : 0.4})

# definitions of all the functions
f_global_VO2 = "VO2)"
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
f_ven_O2 = "O2_art - (Organ_Weight * SMRO2) / BF"
f_ven_CO2 = "CO2_art + (Organ_Weight * SMRCO2) / BF"
f_ven_lac = "lac_art + Organ_Weight * (SMRglu - SMRglu_prod) / BF"
# TODO convert to fractional weight :: f_Weight_Organ = "Organ_Weight "

organ_db.purge_table("GlobalFunctions")
global_function_table = organ_db.table("GlobalFunctions")
global_function_table.insert({"VCO2": "Heart.get_local_vals()[\'VCO2\'] + Brain.get_local_vals()[\'VCO2\'] + Skeletal_muscle.get_local_vals()[\'VCO2\'] + Liver.get_local_vals()[\'VCO2\'] + Kidneys.get_local_vals()[\'VCO2\']"})
global_function_table.insert({"VO2": "Heart.get_local_vals()[\'VO2\'] + Brain.get_local_vals()[\'VO2\'] + Skeletal_muscle.get_local_vals()[\'VO2\'] + Liver.get_local_vals()[\'VO2\'] + Kidneys.get_local_vals()[\'VO2\']"})
global_function_table.insert({"RQ": "VCO2 / VO2"})

organ_db.purge_table("SystemicOrgans")
systemic_organ_table = organ_db.table("SystemicOrgans")
systemic_organ_table.insert({"name": "Skeletal_muscle", "functions": {"VO2": f_VO2, "VCO2": f_VCO2, "SMRCO2": f_SMRCO2, "Venous Glucose": f_ven_glu, "Venous O2": f_ven_O2, "Venous CO2": f_ven_CO2, "Venous Lac": f_ven_lac},
                             "variables": {"BF": [0, 1, 0.6], "SMRO2": [0, 0.5, 0.18], "Organ_Weight" : [10, 50, 27], "VO2": [10, 70, 48.6], "RQ": [0.40, 1, 0.85], "VCO2": [ 10, 60, 41.31], "SMRglu": [0, 0, 0], "SMRglu_prod": [0, 0, 0]}})
systemic_organ_table.insert({"name": "Adipose_tissue", "functions": {"VO2": f_VO2, "VCO2": f_VCO2, "SMRCO2": f_SMRCO2, "Venous Glucose": f_ven_glu, "Venous O2": f_ven_O2, "Venous CO2": f_ven_CO2, "Venous Lac": f_ven_lac},
                             "variables": {"BF": [0, 0.6, 0.2], "SMRO2": [0, 0.5, 0.07], "Organ_Weight" : [5, 100, 18], "VO2": [5, 20, 12.6], "RQ": [0, 1, 1], "SMRglu": [0, 0, 0], "SMRglu_prod": [0, 0, 0]}})
systemic_organ_table.insert({"name": "Skin", "functions": {"VO2": f_VO2, "SMRCO2": f_SMRCO2, "Venous Glucose": f_ven_glu, "Venous O2": f_ven_O2, "Venous CO2": f_ven_CO2, "Venous Lac": f_ven_lac},
                             "variables": {"BF": [0, 1, 0.5], "SMRO2": [0, 0.5, 0.3], "Organ_Weight" : [7, 14, 10], "VO2": [10, 60, 30], "RQ": [0, 1, 0.9], "VCO2": [10, 40, 27], "SMRglu": [0, 0, 0], "SMRglu_prod": [0, 0, 0]}})
systemic_organ_table.insert({"name": "Bones", "functions": {"VO2": f_VO2, "Venous Glucose": f_ven_glu, "Venous O2": f_ven_O2, "Venous Lac": f_ven_lac},
                             "variables": {"BF": [0, 1, 0.1], "SMRO2": [0, 0.4, 0.02], "Organ_Weight" : [5, 12, 8], "VO2": [0.4, 13, 1.6], "SMRglu": [0, 0, 0], "SMRglu_prod": [0, 0, 0]}})
systemic_organ_table.insert({"name": "Blood", "functions": {"VO2": f_VO2, "Venous Glucose": f_ven_glu, "Venous O2": f_ven_O2, "Venous Lac": f_ven_lac},
                             "variables": {"BF": [0, 0, 0], "SMRO2": [0, 0, 0], "Organ_Weight" : [2, 10, 5], "VO2": [0, 0, 0] , "WQ": [0, 1, 1], "SMRglu": [0, 0, 0], "SMRglu_prod": [0, 0, 0]}})
systemic_organ_table.insert({"name": "Gut", "functions": {"VO2": f_VO2},
                             "variables": {"SMRO2": [0, 1, 0.1], "Organ_Weight" : [3, 10, 5], "VO2": [2, 5, 3]}})
systemic_organ_table.insert({"name": "Liver", "functions": {"VO2": f_VO2, "VCO2": f_VCO2, "SMRCO2": f_SMRCO2, "Venous Glucose": f_ven_glu, "Venous O2": f_ven_O2, "Venous CO2": f_ven_CO2, "Venous Lac": f_ven_lac},
                             "variables" : {"BF": [0, 3, 1.5], "SMRO2": [0, 4, 2.2], "Organ_Weight" : [0.4, 6, 1.4], "VO2": [15, 50, 30.8], "RQ": [0, 1, 0.8], "VCO2": [10, 35, 24.64], "SMRglu": [0, 0, 0], "SMRglu_prod": [0, 0, 0]}})
systemic_organ_table.insert({"name": "Brain", "functions": {"VO2": f_VO2, "VCO2": f_VCO2, "SMRCO2": f_SMRCO2, "Venous Glucose": f_ven_glu, "Venous O2": f_ven_O2, "Venous CO2": f_ven_CO2, "Venous Lac": f_ven_lac},
                             "variables" : {"BF": [0, 2, 1], "SMRO2": [0, 5, 3.7], "Organ_Weight" : [1, 2, 1.3], "VO2": [14, 60, 48.1], "RQ": [0, 1, 1], "WQ": [0, 0, 0], "VCO2": [20, 70, 48.1], "SMRglu": [0, 0, 0], "SMRglu_prod": [0, 0, 0]}})
systemic_organ_table.insert({"name": "Heart", "functions": {"VO2": f_VO2, "VCO2": f_VCO2, "SMRCO2": f_SMRCO2, "Venous Glucose": f_ven_glu, "Venous O2": f_ven_O2, "Venous CO2": f_ven_CO2, "Venous Lac": f_ven_lac},
                             "variables" : {"BF": [0, 1, 0.125], "SMRO2": [0, 20, 11], "Organ_Weight" : [0.25, 0.45, 0.31], "VO2": [10, 50, 34.1], "RQ": [0, 1, 0.75], "WQ": [0, 0, 0], "VCO2": [10, 40, 25.575], "SMRglu": [0, 0, 0], "SMRglu_prod": [0, 0, 0]}})
systemic_organ_table.insert({"name": "Diaphragm", "functions": {"VO2": f_VO2, "SMRCO2": f_SMRCO2, "Venous O2": f_ven_O2, "Venous CO2": f_ven_CO2, "Venous Lac": f_ven_lac},
                             "variables" : {"BF": [0, 0.02, 0.01], "SMRO2": [0, 10, 1], "Organ_Weight" : [0.2, 0.5, 0.31], "VO2": [1, 10, 3], "SMRglu": [0, 0, 0], "SMRglu_prod": [0, 0, 0], "RQ": [0, 1, 1]}})
systemic_organ_table.insert({"name": "Kidneys", "functions": {"VO2": f_VO2, "VCO2": f_VCO2, "SMRCO2": f_SMRCO2, "Venous Glucose": f_ven_glu, "Venous O2": f_ven_O2, "Venous CO2": f_ven_CO2, "Venous Lac": f_ven_lac},
                             "variables" : {"BF": [0, 3, 1], "SMRO2": [0, 10, 6.8], "Organ_Weight" : [0.14, 0.5, 0.29], "VO2": [10, 40, 19.72], "RQ": [0, 1, 0.85], "VCO2": [10, 30, 16.762],  "SMRglu": [0, 0, 0], "SMRglu_prod": [0, 0, 0]}})
systemic_organ_table.insert({"name": "Spleen", "functions": {},
                             "variables": {"Organ_Weight" : [0.08, 0.2, 0.14]}})
systemic_organ_table.insert({"name": "Pancreas", "functions": {},
                             "variables": {"Organ_Weight" : [0.05, 0.3, 0.1]}})
systemic_organ_table.insert({"name": "Thyroid", "functions": {},
                             "variables": {"BF": [0, 0.003, 0.001], "Organ_Weight" : [0.009, 0.02, 0.015]}})

#organ = Organ(systemic_organ_table.all()[0], global_param_table.all(), global_constant_table.all())