from functools import partial


def generic_linear_function(a,b,x):
    return a*x + b

def generic_exp_function(a,b,c,x):
    return c*(b**x) + a

def parse_f_vector(db_result: dict, par_name: str):
    if not db_result:
        return lambda x: x
    parameter = db_result[0]['function_vector'][par_name]
    function_type = parameter['type']
    result = {
        'linear':       generic_linear_function,
        'exponential':  generic_exp_function,
    }[function_type]
    print(result)
    function_coeffs = parameter['coeffs']
    specific_function = partial(result, *function_coeffs)
    return specific_function
