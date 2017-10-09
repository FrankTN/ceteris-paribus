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
    def __init__(self, db_path: str):
        super().__init__()
        self._database = TinyDB(db_path)
        # From the database, get the input parameters.
        global_values = Query()
        self._global_parameters = \
        self._database.table("GlobalParameters").search(global_values.name == "global_values")[0]
        # From the global parameters, retrieve the names of the parameters in the input vector.
        self._input_vector_types = self._global_parameters['input_vector_types']
        self._blood_vol = self._global_parameters['blood_vol']
        self.initialize_basic_organs()

    def initialize_basic_organs(self):
        """ Using the database, this function reads the values for all the organs.
            Currently, the lungs are created, and an other compartment is added to
            simulate the systemic circulation in its entirety.
        """
        # Create systemic circulation as a graph.
        self._systemic_circulation = Graph()
        # Add all organs in the database
        for organ_info in self._database.table("SystemicParameters"):
            self._systemic_circulation.add_vertex(Organ(organ_info))

        # Create pulmonary graph
        self._pulmonary_circulation = Graph()
        # Add all organs which should be linked
        for pulm_info in self._database.table("PulmonaryParameters"):
            self._pulmonary_circulation.add_vertex(Organ(pulm_info))

    def get_pulmonary(self):
        return (self._pulmonary_circulation)

    def get_systemic(self):
        return (self._systemic_circulation)

    def calculate_out(self, v_in: dict, graph: Graph, partition: dict) -> dict:
        """ This function calculates the output of a graph system based on an input vector.
            :param v_in the input vector
            :param graph the list of organs being used
            :param partition the dict containing the fractions of the blood volume each organ receives
        """
        v_out = dict()
        for param in self._input_vector_types:
            v_out[param] = sum({o.calculate(v_in[param], param) for o in graph.vertices()})
            if self._input_vector_types[param] == 'rel':
                v_out[param] = v_out[param]/(self._blood_vol/1000)
                pass
        print(self._blood_vol)
        # TODO define what to do when param is relative
        return v_out

    def add_organ(self, organ: Organ, CO_frac, organ_graph, partition: dict):
        pass



    def make_consistent(self):
        pass

    def check_step_consistency(self, circulation):
        print(circulation.vertices())
        pass

    def close(self):
        self._database.close()

    def get_global(self):
        return self._global_parameters

Model(os.getcwd() + "/db/organ_db.json")