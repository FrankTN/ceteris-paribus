class Organ:
    """The class which represents all organs"""

    def __init__(self, f, name = "Default organ"):
        self._function_vector = f
        self._name = name

    def __str__(self):
        return self._name

    def calculate(self, v_in: dict) -> dict:
        out = dict()
        for element in zip(v_in, self._function_vector):
            val, func = element
            out[element] = func(v_in[val])
        return out
