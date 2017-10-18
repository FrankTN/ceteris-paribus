import math

from tinydb import Query

from organ_templates.organ import Organ
from graph import Graph
from constants import SMR_glu_lung


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

    # TODO update these methods, they should calculate
    def get_art_glu(self):
        return self.glu_art_conc

    def get_art_O2(self):
        return self.ox_art_conc

    def get_art_CO2(self):
        return self.co2_art_conc

    def get_art_lac(self):
        return self.lac_art_conc

    def get_art_FFA(self):
        return self.ffa_art_conc

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
        self.ffa_art_conc = self._global_parameters["lac_art_conc"]
        self._blood_vol = self._global_parameters['blood_vol']
        self.initialize_basic_organs()

    def update_model(self, objectName: str, value):
        self.__setattr__(objectName, value)

    def calculate_spec_VO2(self):
        return self.calculate_total_VO2()/self.get_BW()

    def calculate_spec_VCO2(self):
        return self.calculate_total_VCO2()/self.get_BW()

    def calculate_ven_mix(self):
        total_glu = total_O2 = total_CO2 = total_lac = total_FFA = 0
        for organ in self.get_systemic().vertices():
            BF = organ.get_BF()
            total_glu += organ.get_ven_glu() * BF
            total_O2 += organ.get_ven_O2() * BF
            total_CO2 += organ.get_ven_CO2() * BF
            total_lac += organ.get_ven_lac() * BF
            total_FFA += organ.get_ven_FFA() * BF
        glu_c = total_glu / self.get_CardO()
        O2_c = total_O2 / self.get_CardO()
        CO2_c = total_CO2 / self.get_CardO()
        lac_c = total_lac / self.get_CardO()
        FFA_c = total_FFA / self.get_CardO()
        return (glu_c, O2_c, CO2_c, lac_c, FFA_c)

    def get_CardO(self):
        total_CO = 0
        for organ in self.get_systemic().vertices():
            total_CO += organ.get_BF()
        return total_CO

    def get_pulmonary_SMR(self):
        # TODO it doesnt make sense to iterate over all organs
        SMR_O2 = SMR_CO2 = SMR_lac = SMR_glu = SMR_FFA = 0
        for organ in self.get_pulmonary().vertices():
            # TODO implement volume to weight conversion
            if organ.get_name() == 'lung':
                weight = organ.get_weight()
                SMR_O2 = - self.calculate_total_VO2() / weight
                SMR_CO2 = - self.calculate_total_VCO2() / weight
                SMR_glu = SMR_glu_lung
                SMR_lac = 2 * SMR_glu
                SMR_FFA = 0
        return (SMR_glu, SMR_O2, SMR_CO2, SMR_lac, SMR_FFA)

    def get_BW(self):
        return getattr(self,"BodyWeight", 70)

