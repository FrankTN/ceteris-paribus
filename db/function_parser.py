import ast
import decimal

from PyQt5.QtWidgets import QMessageBox


class EvalWrapper(object):
    def __init__(self, variables : dict):
        self.variables = variables

    def add_vars(self, variables: dict):
        self.variables = {**self.variables, **variables}

    def set_function(self, function: str):
        self.function = function

    def evaluate(self):
        transformer = Transformer(self.variables) # Create syntax tree transformer
        if self.function:
            try:
                tree = ast.parse(self.function, mode='eval')
                transformer.visit(tree)
                return eval(self.function, self.variables)
            except NameError:
                return None
            except ZeroDivisionError:
                # On division by zero we will simply return 0 as an answer
                msg = QMessageBox()
                msg.setWindowTitle("Error")
                self.variables.pop("__builtins__", None)
                printable_vars = self.variables
                variables = {str(x) + ": " + str(self.variables[x]) + "\n" for x in printable_vars.keys()}
                msg.setText("Division by zero, set result of " + self.function + " to 0\n" + "".join(variables))
                msg.exec_()
                return 0
        else:
            raise NameError("Cannot evaluate: no function is defined")


# using the NodeTransformer, you can also modify the nodes in the tree,
# however in this example NodeVisitor could do as we are raising exceptions
# only.
class Transformer(ast.NodeTransformer):
    #TODO refine this, make more restrictive
    def __init__(self, variables):
        self.variables = variables

    ALLOWED_NAMES = {'Decimal', 'None', 'False', 'True'}
    ALLOWED_NODE_TYPES = {
        'Expression', # a top node for an expression
        'BinOp',
        'Add',
        'Mult',
        'Sub',
        'Div',
        'Tuple',      # makes a tuple
        'Call',       # a function call (hint, Decimal())
        'Name',       # an identifier...
        'Load',       # loads a value of a variable with given identifier
        'Str',        # a string literal

        'Num',        # allow numbers too
        'List',       # and list literals
        'Dict',       # and dicts...
        'Subscript',
        'Attribute',
        'Index'
    }

    def visit_Name(self, node):
        if not node.id in self.variables:
            return
            raise RuntimeError("Name access to %s is not allowed" % node.id)

        # traverse to child nodes
        return self.generic_visit(node)

    def generic_visit(self, node):
        nodetype = type(node).__name__
        if nodetype not in self.ALLOWED_NODE_TYPES:
            raise RuntimeError("Invalid expression: %s not allowed" % nodetype)

        return ast.NodeTransformer.generic_visit(self, node)

