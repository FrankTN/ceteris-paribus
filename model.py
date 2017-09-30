from tinydb import Query

from Organ_templates.lungs import Lungs
from Organ_templates.organ import Organ
from Organ_templates.other import Other
from db.db_dumper import *
from graph import Graph


class Model(object):
    """ This class represents the model in the Model-View-Controller architecture.
        It contains two graphs representing the systemic and pulmonary circulation.
        To initialize, a JSON-database is loaded using the TinyDB framework.
    """
    def __init__(self):
        super().__init__()
        db_path = os.getcwd()
        self._database = TinyDB(db_path + '/db/organ_db.json')
        # From the database, get the input parameters.
        global_values = Query()
        self._global_parameters = self._database.table("GlobalParameters").search(global_values.name == "global_values")[0]
        # From the global parameters, retrieve the names of the parameters in the input vector.
        self._input_vector_names = self._global_parameters['input_vector_types']
        self.initialize_basic_organs()


    def initialize_basic_organs(self):
        """ Using the database, this function reads the values for all the organs.
            Currently, the lungs are created, and an other compartment is added to
            simulate the systemic circulation in its entirety.
        """
        # Create pulmonary circulation as a graph.
        self._pulmonary_circulation = Graph()
        self._pulmonary_circulation.add_vertex(Lungs())
        self._pulmonary_partition = {}
        for element in self._database.table("PulmonaryParameters").all():
            self._pulmonary_partition[element['name']] = element['frac']
        # Create systemic circulation graph, add organs using the database.
        self._systemic_circulation = Graph()
        self._systemic_circulation.add_vertex(Other())
        self._systemic_partition = {}
        for element in self._database.table("SystemicParameters").all():
            self._systemic_partition[element['name']] = element['frac']

    def get_pulmonary(self):
        return (self._pulmonary_circulation, self._pulmonary_partition)

    def get_systemic(self):
        return (self._systemic_circulation, self._systemic_partition)

    def calculate_out(self, v_in: dict, graph: Graph, partition: dict) -> dict:
        """ This function calculates the output of a graph system based on an input vector.
            :param v_in the input vector
            :param graph the list of organs being used
            :param partition the dict containing the fractions of the blood volume each organ receives
        """
        v_out = dict()
        for param in self._input_vector_names:
            v_out[param] = sum({o.calculate(v_in[param], param) for o in graph.vertices()})
        # TODO define what to do when param is relative
        return v_out

    def add_organ(self, organ: Organ, CO_frac, organ_graph, partition: dict):
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

    def get_global(self):
        return self._global_parameters


# Start of the main script, this will be replaced by a GUI

model = Model()
print(model.calculate_out({"VCO2" : 5000, "VO2" : 5000}, *model.get_pulmonary()))
print(model.calculate_out({"VCO2" : 5000, "VO2" : 5000}, *model.get_systemic()))
model.add_organ(Organ("heart", "SystemicParameters"),0.04,*model.get_systemic())
print(model.calculate_out({"VCO2" : 5000, "VO2" : 5000}, *model.get_systemic()))
dump_model(model, "test.json")
print(model.check_global_consistency())