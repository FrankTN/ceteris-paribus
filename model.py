from Organ_templates.organ import Organ
from Organ_templates.lungs import Lungs
from graph import Graph

class Model(Graph):
    def __init__(self):
        super().__init__()

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
        CO_partition = [1,1]
        v_all_out = list()
        for (index, organ) in enumerate(self.vertices()):
            v_in_specific = {k : v * CO_partition[index] for k, v in v_in.items()}
            v_all_out.append(organ.calculate(v_in_specific))
        v_out = self.combine_outputs(v_all_out)
        return v_out

    def make_consistent(self):
        pass

# Start of the main script

model = Model()
lungs = Organ()
other = Organ()
model.add_organ(lungs)
model.add_organ(other)
print(model.calculate_out({"VCO2" : 5000, "VO2" : 5000}))
lungs = Lungs()
