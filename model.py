import os
from tinydb import TinyDB, Query

from Organ_templates.lungs import Lungs
from Organ_templates.organ import Organ
from Organ_templates.other import Other
from graph import Graph

class Model:
    def __init__(self):
        super().__init__()
        db_path = os.getcwd()
        self._database = TinyDB(db_path + '/db/organ_db.json')
        global_values = Query()
        self._global_parameters = self._database.table("GlobalParameters").search(global_values.name == "global_values")[0]
        self._input_vector = self._global_parameters['input_vector']
        self.initialize_basic_organs()

    def initialize_basic_organs(self):
        self._pulmonary_circulation = Graph()
        self._pulmonary_circulation.add_vertex(Lungs())
        self._pulmonary_partition = {}
        for element in self._database.table("PulmonaryParameters").all():
            self._pulmonary_partition[element['name']] = element['frac']
        self._systemic_circulation = Graph()
        self._systemic_circulation.add_vertex(Other())
        self._systemic_partition = {}
        for element in self._database.table("SystemicParameters").all():
            self._systemic_partition[element['name']] = element['frac']

    def combine_outputs(self, v_all_out: list) -> dict:
        v_out = dict.fromkeys(v_all_out[0].keys(), 0)
        for vector in v_all_out:
            for element in vector:
                v_out[element] += vector[element]
        return v_out

    def get_pulmonary(self):
        return (self._pulmonary_circulation, self._pulmonary_partition)

    def get_systemic(self):
        return (self._systemic_circulation, self._systemic_partition)

    def calculate_out(self, v_in : dict, graph : Graph, partition : dict) -> dict:
        v_all_out = list()
        for organ in graph.vertices():
            v_in_specific = {k : v * partition[organ.name] for k, v in v_in.items()}
            v_all_out.append(organ.calculate(v_in_specific))
        v_out = self.combine_outputs(v_all_out)
        return v_out

    def add_organ(self, organ, CO_frac, organ_graph, partition : dict):
        divided_frac = CO_frac / len(organ_graph.vertices())
        organ_graph.add_vertex(organ)
        for element in partition:
            partition[element] = partition[element] - divided_frac
        partition[organ.name] = CO_frac



    def make_consistent(self):
        pass

    def check_step_consistency(self):
        pass

    def check_global_consistency(self):
        systemic_sum = sum(self._systemic_partition.values())
        print(systemic_sum)
        pulmonary_sum = sum(self._pulmonary_partition.values())
        correct_fractions = systemic_sum + pulmonary_sum == 2
        return correct_fractions

# Start of the main script

model = Model()
print(model.calculate_out({"VCO2" : 5000, "VO2" : 5000}, *model.get_pulmonary()))
print(model.calculate_out({"VCO2" : 5000, "VO2" : 5000}, *model.get_systemic()))
model.add_organ(Organ("heart", "SystemicParameters"),0.04,*model.get_systemic())
print(model.calculate_out({"VCO2" : 5000, "VO2" : 5000}, *model.get_systemic()))

print(model.check_global_consistency())