from PyQt5.QtWidgets import QMessageBox


class EvalWrapper(object):
    def __init__(self, variables : dict):
        self.variables = variables

    def add_vars(self, variables: dict):
        self.variables = {**self.variables, **variables}

    def set_function(self, function: str):
        self.function = function

    def evaluate(self):
        if self.function:
            try:
                return eval(self.function, self.variables)
            except NameError:
                return None
            except ZeroDivisionError:
                # On division by zero we will simply return 0 as an answer
                msg = QMessageBox()
                msg.setWindowTitle("Error")
                printable_vars = self.variables
                printable_vars.pop('__builtins__', None)
                variables = {str(x) + ": " + str(self.variables[x]) + "\n" for x in printable_vars.keys()}
                msg.setText("Division by zero, set result of " + self.function + " to 0\n" + "".join(variables))
                msg.exec_()
                return 0
        else:
            raise NameError("Cannot evaluate: no function is defined")
