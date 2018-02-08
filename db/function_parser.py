import ast

from PyQt5.QtWidgets import QMessageBox


class EvalWrapper(object):
    def __init__(self, variables, transformer):
        self.variables = variables
        self.transformer = transformer
        self.function = None

    def add_vars(self, variables):
        # This functions adds new values to the var dict which is already present in the object
        self.variables = {**self.variables, **variables}

    def set_function(self, function):
        self.function = function

    def evaluate(self):
        self.transformer.set_variables(self.variables)  # Create syntax tree transformer
        if self.function:
            try:
                tree = ast.parse(self.function, mode='eval')
                self.transformer.visit(tree)
                clause = compile(tree, '<AST>', 'eval')
                # make the globals contain only the Decimal class,
                # and eval the compiled object
                return eval(clause, self.variables)
            except SyntaxError:
                # On division by zero we will simply return 0 as an answer
                msg = QMessageBox()
                msg.setWindowTitle("Error")
                msg.setText("Invalid Syntax")
                msg.exec_()
                return None
            except NameError:
                return None
            except TypeError:
                # We are missing an operand because it is undefined, this is the same as having a NameError in the eval
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


# Using the NodeTransformer, you can also modify the nodes in the tree,
# however in this example NodeVisitor could do as we are raising exceptions
# only.
class Transformer(ast.NodeTransformer):

    def set_variables(self, variables):
        self.variables = variables

    ALLOWED_NAMES = {'Decimal', 'None', 'False', 'True'}
    ALLOWED_NODE_TYPES = {
        'Expression',  # a top node for an expression
        'BinOp',
        'Add',
        'Mult',
        'Sub',
        'Div',
        'Call',  # a function call (hint, Decimal())
        'Name',  # an identifier...
        'Load',  # loads a value of a variable with given identifier
        'Str',  # a string literal

        'Num',  # allow numbers too
        'Subscript',
        'Attribute',
        'Index'
    }

    def generic_visit(self, node):
        nodetype = type(node).__name__
        if nodetype not in self.ALLOWED_NODE_TYPES:
            raise SyntaxError("Invalid expression: %s not allowed" % nodetype)
        # if node

        return ast.NodeTransformer.generic_visit(self, node)


class ModelTransformer(Transformer):
    """ Works as an extension of the regular Transformer. This transformer is only used by the model to keep track of
        the values being visited.
        """

    def __init__(self, vars):
        self.visited = {}
        self.current_node = ""
        self.variables = vars

    def visit_Name(self, node):
        self.visited[node.id] = ""
        self.current_node = node.id
        if node.id not in self.variables.keys():
            raise NameError
        return self.generic_visit(node)

    def visit_Str(self, node):
        self.visited[self.current_node] = node.s
        return self.generic_visit(node)
