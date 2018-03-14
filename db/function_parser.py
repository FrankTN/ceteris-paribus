import ast

from PyQt5.QtWidgets import QMessageBox


class EvalWrapper(object):
    def __init__(self, variables, transformer, organ_name=None):
        self.variables = variables
        self.transformer = transformer
        self.function = None
        self.function_name = None
        self.organ_name = organ_name

    def add_vars(self, variables):
        # This functions adds new values to the var dict which is already present in the object
        self.variables = {**self.variables, **variables}

    def set_function(self, function_str):
        self.function = function_str

    def set_organ_name(self, organ_name):
        self.organ_name = organ_name

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
                if self.organ_name is not None:
                    message = " in " + self.organ_name
                else:
                    message = ""
                msg.setText("Division by zero, we are setting the value of " + self.function_name + message + " to 0\n")
                msg.exec_()
                return 0
        else:
            raise NameError("Cannot evaluate: no function is defined")

    def set_function_name(self, function_name):
        self.function_name = function_name


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


def evaluate_functions(functions, variables, prerequisites=None):
    """
    This function calculates the global outputs of the model
    :return: a dictionary containing the names of the outputs and their calculated values.
    """
    # Make a shallow copy of the global function dict, so that we can freely modify it
    changed = True
    output = {}

    while changed:
        changed = False
        for function_name in list(functions):
            # For every unresolved functions, we create an evaluator object

            evaluator = EvalWrapper(variables, ModelTransformer(variables))
            new_func = functions[function_name]
            evaluator.set_function(new_func)
            evaluator.set_function_name(function_name)
            # The result of the evaluation is stored in the result variable if it exists
            result = evaluator.evaluate()
            if prerequisites is not None:
                # We are also supposed to store the required values as a side effect
                required_vals = evaluator.transformer.visited
                prerequisites[function_name] = required_vals

            if result is not None:
                # We have found a new result, therefore, we set changed to True and we store the result
                changed = True
                variables[function_name] = result
                output[function_name] = result
                # Finally, we remove the function we just resolved from the globals so that we don't loop infinitely
                functions.pop(function_name)
    if functions:
        msg = QMessageBox()
        msg.setWindowTitle("Error")
        unresolved_string = {str(x) + ": " + functions[x] + "\n" for x in functions.keys()}
        msg.setText(
            "The specified database cannot create the model,\nplease look at the following unresolvable functions: \n" + "".join(
                unresolved_string))
        msg.exec_()
        quit(-1)
    return output
