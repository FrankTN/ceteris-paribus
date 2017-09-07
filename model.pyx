import math as ma
import numpy as np

import inputhandler

def calculateV_O_2_WR(WR):
    """Using the Work Rate (WR), we calculate the VO2"""
    # We assume a resting VO_2 of 200 ml/min. This agrees with experimental data in young males.
    VO_2_Rest = 200
    # Similarly, we have a VO_2_Unloaded of 400 ml/min
    VO_2_Unloaded = 400
    # Alpha is given at 10 ml/min/W
    alpha = 10
    # Finally, we can calculate the predicted VO_2 based on the Work Rate
    V_O_2_WR = VO_2_Rest + VO_2_Unloaded + alpha * WR
    return V_O_2_WR

def calculate_La(V_O_2_WR):
    # This formula requires an input in L, so we have to perform a conversion
    V_O_2_WR_L = V_O_2_WR / 1000
    # A normally distributed noise term can be added.
    epsilon = np.random.normal(0,1,1)
    # TODO define proper Betas
    beta_0 = 0
    beta_1 = 1
    conc_La = ma.exp(beta_0 + beta_1 * V_O_2_WR_L + epsilon)
    return conc_La

WR = inputhandler.startup()
V_O_2_WR = calculateV_O_2_WR(WR)
predicted_La = calculate_La(V_O_2_WR)
print(predicted_La)

#TODO link muscle [La] to blood concentration