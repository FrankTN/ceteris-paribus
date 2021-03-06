from PyQt5.QtGui import QValidator

from ceteris_paribus.db.function_parser import EvalWrapper, Transformer, ModelTransformer


class Validator(QValidator):
    def __init__(self):
        # The confirmed bool is used to signal when input is final
        super().__init__()
        self.confirmed = False

    def set_confirmed(self, bool_value):
        self.confirmed = bool_value

    def validate(self, p_str, p_int):
        # Check that the function, present in the p_str argument as a string, is actually valid
        self.evaluator.set_function(p_str)
        if self.evaluator.function:
            if self.confirmed:
                # If we reach this it means the user has confirmed the input, we validate
                if self.evaluator.evaluate():
                    return QValidator.Acceptable, p_str, p_int
                else:
                    return QValidator.Invalid, p_str, p_int
            return QValidator.Intermediate, p_str, p_int
        else:
            return QValidator.Intermediate, p_str, p_int


class LocalFunctionValidator(Validator):
    """ When a function is entered by the user to be added to an organ this validator checks whether the function can
        actually be evaluated."""
    def __init__(self, variables, organ_name):
        super().__init__()

        # self.functions = functions
        self.evaluator = EvalWrapper(variables, Transformer(), organ_name)


class GlobalFunctionValidator(Validator):
    def __init__(self, vars, function_name):
        super().__init__()
        self.evaluator = EvalWrapper(vars, ModelTransformer(vars))
        self.evaluator.set_function_name(function_name)
