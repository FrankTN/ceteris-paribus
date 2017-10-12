# Start of the main script, this will be replaced by a GUI
import sys
from PyQt5.QtCore import QFileSelector
from PyQt5.QtWidgets import QApplication

from organ_templates.organ import Organ
from db.db_dumper import dump_model
from model import Model, os


def load_db(db_path: str) -> bool:
    if os.path.exists(db_path) and os.path.splitext(db_path)[1] == ".json":
        model = Model(db_path)

        print(model.calculate_out({"VCO2": 5000, "VO2": 5000}, *model.get_pulmonary()))
        print(model.calculate_out({"VCO2": 5000, "VO2": 5000}, *model.get_systemic()))
        model.add_organ(Organ("heart", "SystemicParameters"), 0.04, *model.get_systemic())
        print(model.calculate_out({"VCO2": 5000, "VO2": 5000}, *model.get_systemic()))
        dump_model(model, "test.json")
        print(model.check_global_consistency())
        return True

    else:
        # TODO this does not make sense
        return False
