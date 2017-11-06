from PyQt5.QtGui import QValidator

from db.function_parser import EvalWrapper


class FunctionValidator(QValidator):
    def __init__(self, variables):
        super().__init__()
        self.evaluator = EvalWrapper(variables)
        self.confirmed = False

    def setConfirmed(self, bool_value):
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
