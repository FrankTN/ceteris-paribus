import operator

from graph import Graph
from organ import Organ


class Model(Graph):
    def __init__(self):
        super().__init__()

    def add_organ(self, organ):
        super().add_vertex(organ)
        self.make_consistent()

    def combine_outputs(self, v_single_out: dict):
        v_out = [0,0,0]
        print(v_single_out)
        v_out = list(map(operator.add, v_out, v_single_out.values()))
        return v_out

    def calculate_out(self, v_in : dict):
        x = dict()
        for o in self.vertices():
            x.update(o.calculate(v_in))
        v_out = self.combine_outputs(x)
        return v_out

    def make_consistent(self):
        pass

model = Model()
lungs = Organ([lambda vco2: vco2 + 200, lambda vo2: vo2 + 200],"Lungs")
other = Organ([lambda vco2: vco2 - 200, lambda vo2: vo2 - 200],"Other")
model.add_organ(lungs)
model.add_organ(other)
print(model.calculate_out({"VCO2" : 5000, "VO2" : 5000}))
