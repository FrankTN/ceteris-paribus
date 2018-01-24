from PyQt5.QtGui import QValidator

from db.function_parser import EvalWrapper, Transformer


class FunctionValidator(QValidator):
    """ When a function is entered by the user to be added to an organ this validator checks whether the function can
        actually be evaluated."""
    def __init__(self, variables):
        super().__init__()

        self.evaluator = EvalWrapper(variables, Transformer())
        # The confirmed bool is used to signal when input is final
        self.confirmed = False

    def set_confirmed(self, bool_value):
        self.confirmed = bool_value

    def validate(self, p_str, p_int):
        self.evaluator.set_function(p_str)
        if self.evaluator.function:
            if self.confirmed:
                if self.evaluator.evaluate():
                    return QValidator.Acceptable, p_str, p_int
                else:
                    return QValidator.Invalid, p_str, p_int
            return QValidator.Intermediate, p_str, p_int
        else:
            return QValidator.Intermediate, p_str, p_int
