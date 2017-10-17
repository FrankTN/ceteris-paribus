import math

from tinydb import Query

from organ_templates.organ import Organ
from graph import Graph


class Model(object):
    """ This class represents the model in the Model-View-Controller architecture.
        It contains two lists of organs representing the systemic and pulmonary circulation.
        To initialize, a JSON-database is loaded using the TinyDB framework.
    """
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.initialize_globals()


    def initialize_basic_organs(self):
        """ Using the database, this function reads the values for all the organs.
            Currently, the lungs are created, and an other compartment is added to
            simulate the systemic circulation in its entirety.
        """
        # Create systemic circulation as a graph.
        self._systemic_circulation = Graph()
        # Add all organs in the database
        for organ_info in self._database.table("SystemicParameters"):
            self._systemic_circulation.add_vertex(Organ(organ_info, self))

        # Create pulmonary graph
        self._pulmonary_circulation = Graph()
        # Add all organs which should be linked
        for pulm_info in self._database.table("PulmonaryParameters"):
            self._pulmonary_circulation.add_vertex(Organ(pulm_info, self))

    def get_pulmonary(self):
        return self._pulmonary_circulation

    def get_systemic(self):
        return self._systemic_circulation

    def check_global_consistency(self):
        """ This function will validate the model after each change"""
        total_VO2 = 0
        total_VCO2 = 0
        for organ in self._systemic_circulation.vertices():
            total_VO2 += float(organ.get_VO2())
            total_VCO2 += float(organ.get_VCO2())
        for organ in self._pulmonary_circulation.vertices():
            total_VO2 += organ.get_VO2()
            total_VCO2 += organ.get_VCO2()
        VO2_consistent = math.isclose(total_VCO2, 0, abs_tol=0.00001)
        VCO2_consistent = math.isclose(total_VO2, 0, abs_tol=0.00001)
        return VO2_consistent and VCO2_consistent

    def close(self):
        self._database.close()

    def get_global_values(self):
        return self._global_parameters

    def calculate_total_VO2(self):
        """ Return the oxygen consumption for the whole body in mL/min """
        total_VO2 = 0
        for organ in self._systemic_circulation.vertices():
            total_VO2 += float(organ.get_VO2())
        return total_VO2

    def calculate_total_VCO2(self):
        """ Return the CO2 consumption in mL/min"""
        total_VCO2 = 0
        for organ in self._systemic_circulation.vertices():
            total_VCO2 += float(organ.get_VCO2())
        return total_VCO2

    def calculate_total_RQ(self):
        """ Calculates the Respiratory Quotient of the entire body"""
        return self.calculate_total_VCO2()/self.calculate_total_VO2()

    def globalChanged(self, changeSender):
        self.setGlobal(changeSender.objectName, changeSender.value)

    def setGlobal(self, objectName, value):
        #Todo implement
        pass

    # TODO update these methods, they should calculate
    def get_art_glu(self):
        return self.glu_art_conc

    def get_art_O2(self):
        return self.ox_art_conc

    def get_art_CO2(self):
        return self.co2_art_conc

    def get_art_lac(self):
        return self.lac_art_conc

    def get_organ(self, index):
        return self.get_systemic().vertices()[index]

    def initialize_globals(self):
        # Since we only create a model after we know that the db has been loaded, we know that getdb() works
        self._database = self.controller.get_db()
        # From the database, get the input parameters.
        global_values = Query()
        self._global_parameters = \
            self._database.table("GlobalParameters").search(global_values.name == "global_values")[0]
        self.glu_art_conc = self._global_parameters["glu_art_conc"]
        self.lac_art_conc = self._global_parameters["lac_art_conc"]
        self.ox_art_conc = self._global_parameters["ox_art_conc"]
        self.co2_art_conc = self._global_parameters["co2_art_conc"]
        self._blood_vol = self._global_parameters['blood_vol']
        self.initialize_basic_organs()
