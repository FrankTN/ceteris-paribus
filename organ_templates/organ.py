import constants
from db.function_parser import EvalWrapper


class Organ(object):
    """The class which represents all organs"""

    def __init__(self, organ_info: dict, global_values : dict):
        """ This generic implementation of an organ in the model uses the __setattr__ method to add attributes.
            Adding attributes in this way is necessary since not all attributes are defined for each organ.
        """
        self.global_values = global_values
        if organ_info:
            for property in organ_info.keys():
                self.__setattr__(property, organ_info[property])

        print(self.__dict__)
        self.defined_variables = {**getattr(self,'vars'), **getattr(self,'global_values')}
        self.results = {}
        self.evaluate()

    def evaluate(self):
        evaluator = EvalWrapper(self.defined_variables)
        function_dict = getattr(self, 'functions')
        for function_name in function_dict:
            evaluator.set_function(function_dict[function_name])
            self.results[function_name] = evaluator.evaluate()

    def get_name(self):
        return getattr(self, 'name', 'default_organ')

    def get_vars(self):
        return self.defined_variables

    def get_VO2(self):
        return getattr(self, 'VO2', 0)

    def get_VCO2(self):
        return getattr(self, 'VCO2', 0)

    def calculate_VO2(self):
        """ Calculate the consumption of oxygen by the organ in mL/min"""
        # TODO implement conversion from volume to weight
        if hasattr(self,"CMRO2") and hasattr(self, "volume"):
            return 10 * constants.mol_to_ml_37_deg * self.CMRO2 * self.volume
        else:
            return 0

    def calculate_VCO2(self):
        """ Calculate the production of CO2 by the organ."""
        if hasattr(self, "CMRCO2") and hasattr(self, "volume"):
            return 10 * constants.mol_to_ml_37_deg * self.CMRCO2 * self.volume
        else:
            return 0

    def calculate_CMRCO2(self):
            """ Calculate the production of CO2"""
            return self.get_RQ() * self.get_SMR_O2()

    def get_SMR_glu_oxidation(self):
        return self.get_WQ() * self.get_SMR_glu()

    def get_SMR_lac(self):
        return 2 * self.get_WQ() * self.get_SMR_glu()

    def __str__(self):
        return str(getattr(self, 'name', 'default_organ')) + ":\n\tFunctions: " + str(getattr(self, 'functions')) + "\n\tVars: " + str(getattr(self, 'vars'))

    def get_RQ(self):
        """ Calculate the Respiratory Quotient of the organ"""
        if self.calculate_VCO2() == 0:
            return 0
        else:
            return self.calculate_VO2() / self.calculate_VCO2()

    def get_WQ(self):
        """ This function returns the Warburg Coefficient of the organ. This coefficient defines the glucose fraction
            being converted to CO2 as opposed to HLa"""
        return getattr(self, 'WQ', 0)

    def get_ven_glu(self):
        return self.model.get_art_glu() - (10 * self.get_weight() - (self.get_SMR_glu() - self.get_SMR_glu_prod()) / self.get_BF())

    def get_ven_O2(self):
        return self.model.get_art_O2() - (10 * self.get_weight() * self.get_SMR_O2() / self.get_BF())

    def get_ven_CO2(self):
        return self.model.get_art_CO2() + (10 * self.get_weight() * self.get_SMR_O2() / self.get_BF())

    def get_ven_lac(self):
        return self.model.get_art_lac() + (10 * self.get_weight() * (self.get_SMR_lac() - self.get_SMR_lac_conc()) / self.get_BF())

    def get_ven_FFA(self):
        return self.model.get_art_FFA() - (10 * self.get_weight() * self.get_SMR_FFA()) / self.get_BF()

    def get_SMR_glu(self):
        return getattr(self, "CMR_glu", 0)

    def get_weight(self):
        return getattr(self, "Wfrac", 0) * self.model.get_BW()

    def get_BF(self):
        return getattr(self, "BF", 5)

    def get_SMR_O2(self):
        """ Returns the specific metabolic consumption of oxygen in mmol/min/100g """
        return getattr(self, "CMRO2", 0)

    def get_SMR_glu_prod(self):
        return getattr(self, "CMR_glu_prod", 0)

    def get_SMR_lac_conc(self):
        return getattr(self, "CMR_lac_cons", 0)

    def get_SMR_FFA(self):
        return 6 * (1 - self.get_RQ()) / (27 * self.get_RQ() - 18) * self.get_SMR_glu()


