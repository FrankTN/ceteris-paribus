import constants

class Organ(object):
    """The class which represents all organs"""

    def __init__(self, organ_info: dict):
        """ This generic implementation of an organ in the model uses the __setattr__ method to add attributes.
            Adding attributes in this way is necessary since not all attributes are defined for each organ.
        """
        for property in organ_info.keys():
            self.__setattr__(property, organ_info[property])

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
            return None

    def calculate_VCO2(self):
        """ Calculate the production of CO2 by the organ."""
        if hasattr(self, "CMRCO2") and hasattr(self, "volume"):
            return 10 * constants.mol_to_ml_37_deg * self.CMRCO2 * self.volume
        else:
            return None

    def calculate_CMRCO2(self):
            """ Find the consumption"""
            return self.calculate_RQ() * self.calculate_CMRO2()

    def calculate_CMR_oxidation_glu(self):
        return self.getWQ() * self.getCMR_glu()

    def calculate_CMR_lac(self):
        return 2 * self.getWQ() * self.getCMR_glu()

    def __str__(self):
        return getattr(self, 'name', 'default_organ')

    def calculate_RQ(self):
        """ Calculate the Respiratory Quotient of the organ"""
        return self.calculate_VO2() / self.calculate_VCO2()

    def calculate_CMRO2(self):
        """ Calculates the specific metabolic consumption of oxygen in mmol/min/100g """
        if hasattr(self, "CMRO2"):
            return self.CMRO2
        else:
            return None

    def getWQ(self):
        """ This function returns the Warburg Coefficient of the organ. This coefficient defines the glucose fraction
            being converted to CO2 as opposed to HLa"""
        if hasattr(self, "WQ"):
            return self.WQ
        else:
            return None

    def calculate_ven_glu(self):
        return self.get_art_glu() - (10 * self.getWeight() - (self.getCMR_glu() - self.getCMR_glu_prod()) / self.getBF())

    def calculate_ven_O2(self):
        return self.get_art_O2() - (10 * self.getWeight() * self.getCMRO2() / self.getBF())

    def calculate_ven_CO2(self):
        return self.get_art_CO2() + (10 * self.getWeight() * self.getCMRO2() / self.getBF())

    def calculate_ven_lac(self):
        return self.get_art_lac() + (10 * self.getWeight() * (self.getCMR_lac() - self.getCMR_lac_cons()) / self.getBF())

    def getCMR_glu(self):
        if hasattr(self, "CMR_glu"):
            return self.CMR_glu
        else:
            return None

    def getWeight(self):
        return getattr(self, "weight", 0)

    def getBF(self):
        return getattr(self, "BF", 0)

    def get_art_glu(self):
        return getattr(self, "art_glu", 0)

    def get_art_O2(self):
        return getattr(self, "art_O2", 0)

    def get_art_CO2(self):
        return getattr(self, "art_CO2", 0)

    def getCMRO2(self):
        return getattr(self, "CMRO2", 0)

    def get_art_lac(self):
        return getattr(self, "art_lac", 0)

    def getCMR_lac(self):
        return getattr(self, "CMR_lac", 0)

    def getCMR_glu_prod(self):
        return getattr(self, "CMR_glu_prod", 0)

    def getCMR_lac_cons(self):
        return getattr(self, "CMR_lac_cons", 0)










