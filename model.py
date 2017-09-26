import os
from tinydb import TinyDB, Query

from Organ_templates.lungs import Lungs
from Organ_templates.other import Other
from graph import Graph

class Model(Graph):
    def __init__(self):
        super().__init__()
        db_path = os.getcwd()
        self._database = TinyDB(db_path + '/db/organ_db.json')
        global_values = Query()
        self._global_parameters = self._database.table("GlobalParameters").search(global_values.name == "global_values")

    def add_organ(self, organ):
        super().add_vertex(organ)
        self.make_consistent()

    def combine_outputs(self, v_all_out: list) -> dict:
        v_out = dict.fromkeys(v_all_out[0].keys(), 0)
        for vector in v_all_out:
            for element in vector:
                v_out[element] += vector[element]
        return v_out

    def calculate_out(self, v_in : dict) -> dict:
        v_all_out = list()
        for organ in self.vertices():
            v_in_specific = {k : v * organ.frac for k, v in v_in.items()}
            v_all_out.append(organ.calculate(v_in_specific))
        v_out = self.combine_outputs(v_all_out)
        return v_out

    def make_consistent(self):
        pass

    def check_step_consistency(self):
        pass

    def check_global_consistency(self):
        return sum(list(map(lambda organ: organ.frac, self.vertices()))) == 2


# Start of the main script

model = Model()
lungs = Lungs()
other = Other()
model.add_organ(lungs)
model.add_organ(other)
print(model.calculate_out({"VCO2" : 5000, "VO2" : 5000}))
print(model.check_global_consistency())