from functools import partial


def generic_linear_function(a,b,x):
    return a*x + b

def generic_exp_function(a,b,c,x):
    return c*(b**x) + a

def parse_f_vector(db_result: dict):
    if not db_result:
        return lambda x: x
    function_type = db_result['type']
    result = {
        'linear':       generic_linear_function,
        'exponential':  generic_exp_function,
    }[function_type]
    function_coeffs = db_result['coeffs']
    specific_function = partial(result, *function_coeffs)
    return specific_function

def create_functions(function_vector_list: dict):
    return {k: parse_f_vector(v) for k, v in function_vector_list.items()}