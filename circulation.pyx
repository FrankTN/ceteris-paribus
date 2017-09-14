import math as ma

class circulation:

    def __init__(self):
        self._predicted_La =  0.0 #For testing, initialize lactate as 0

    @staticmethod
    def calculate_La(V_O_2_WR):
        # This formula requires an input in L, so we have to perform a conversion
        V_O_2_WR_L = V_O_2_WR / 1000

        b = 2.88
        V_O_2_T = 1.51 # L / min
        La_T = 0.65
        _predicted_La = La_T * ma.pow(V_O_2_WR_L / V_O_2_T, b)
        return _predicted_La


    @property
    def get_predicted_La(self):
        return self._predicted_La

