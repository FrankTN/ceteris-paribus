class EvalWrapper(object):
    def __init__(self, variables : dict):
        self.variables = variables

    def add_vars(self, variables: dict):
        self.variables = {**self.variables, **variables}

    def set_function(self, function: str):
        self.function = function

    def evaluate(self):
        if self.function:
            return eval(self.function, self.variables)
        else:
            raise NameError("Cannot evaluate: no function is defined")
