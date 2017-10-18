''' This module contains functions to deal with the serialization and deserialization of functions used by the organs
    in the model. When an organ is loaded, a list of functions defines what the organ does with each of its input
    parameters. This module allows those functions to be created from the JSON database descriptions.
'''
from functools import partial

# A list of template functions used by the organs is defined here. Upon loading the function, the parameters are
# entered and a partial function is returned.
def generic_linear_function(a, b, x):
    return a * x + b


def generic_exp_function(a, b, c, x):
    return c * (b ** x) + a


def parse_f_vector(db_result: dict):
    ''' This function returns a partially applied \'specific function\' using the database dict. This function is used when
        deserializing the database.
    '''
    if not db_result:
        return lambda x: x
    function_type = db_result['type']
    result = {
        'linear': generic_linear_function,
        'exponential': generic_exp_function,
    }[function_type]
    function_coeffs = db_result['coeffs']
    specific_function = partial(result, *function_coeffs)
    return specific_function


def create_functions(function_vector_list: dict):
    '''Create partial functions for all JSON elements in the function_vector'''
    return {k: parse_f_vector(v) for k, v in function_vector_list.items()}


def parse_type(param: partial):
    ''' This does the opposite of the parse_f_vector function. Using a partial function, retrieve its type so we can
        store it in the database during serialization.
    '''
    func_name = str(param.func)[10:].split()[0]
    type = {
        'generic_linear_function': 'linear',
        'generic_exp_function': 'exponential',
    }[func_name]
    return type
