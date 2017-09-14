import math as ma
import numpy as np

import inputhandler
from circulation import circulation

c = circulation()
VO_2 = inputhandler.startup()
predicted_La = c.calculate_La(VO_2)
print("10^" + str(round(ma.log10(predicted_La),3)) + " mmol/L")

#TODO link muscle [La] to blood concentration