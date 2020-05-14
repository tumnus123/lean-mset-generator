# quadratics.py
#---------------

import sympy

def solve_system(a_x, a_y, b_x, b_y, c_x, c_y):
    """Given three points, solve for their quadratic curve

    Keyword args:
    a_x -- the x coordinate of point a
    a_y -- the y coordinate of point a
    b_x -- the x coordinate of point b
    b_y -- the y coordinate of point b
    c_x -- the x coordinate of point c
    c_y -- the y coordinate of point c

    Returns:
    Array of the quadratic's coefficients ==> [a, b, c]
    """

    # Use sympy to solve the system of equations
    a, b, c = sympy.symbols("a b c", real=True)
    eq1 = sympy.Eq( a*a_x**2 + b*a_x + c, a_y )
    eq2 = sympy.Eq( a*b_x**2 + b*b_x + c, b_y )
    eq3 = sympy.Eq( a*c_x**2 + b*c_x + c, c_y )
    sols = sympy.solve([eq1, eq2, eq3], [a, b, c])

    return [sols[a], sols[b], sols[c]]

def build_q_function(cf_a, cf_b, cf_c):
    """Given three coefficients, return the quadratic as a function."""

    def qf(test_x):
        y = sympy.symbols("y", real=True)
        eq1 = sympy.Eq( cf_a*test_x**2 + cf_b*test_x + cf_c, y )
        sol = sympy.solve([eq1], [y])
        return sol[y]

    return qf
