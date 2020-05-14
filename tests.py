# ===========================================
# Tests.py
# Jason Hine
# 8/14/2019
# ===========================================

# ---------------------------
# Math function tests
# ---------------------------
import quadratics as quads
import mandelmaths as mands

print("\nTest 1.1: Solve quadratics with integer coefficients")
print(" Test input xy pairs: (1,3); (2,7); (3,13)")
test_cf = quads.solve_system(1,3,2,7,3,13)
print(f"   Test coeff finder: {test_cf[0]}, {test_cf[1]}, {test_cf[2]} (should be 1,1,1)")
test_qf = quads.build_q_function(test_cf[0], test_cf[1], test_cf[2])
print(" Test output function with x = 2")
test_x = 2
test_y = test_qf(test_x)
print(f"   Test Y: {test_y} (should be 7)")

print("\nTest 1.2: Solve quadratics with non-integer coefficients")
print(" Test input xy pairs: (0.5, 0.8); (1.5, 1.4); (2.5, 3.7)")
test_cf = quads.solve_system(a_x=0.5, a_y=0.8, b_x=1.5, b_y=1.4, c_x=2.5, c_y=3.7)
print(f"   Test coeff finder: {test_cf[0]}, {test_cf[1]}, {test_cf[2]} (should be 0.85, -1.1, 1.1375)")
test_qf = quads.build_q_function(test_cf[0], test_cf[1], test_cf[2])
print(" Test output function with x = 3.3")
test_x = 3.3
test_y = test_qf(test_x)
print(f"   Test Y: {test_y} (should be 6.764)")

# TODO: Solve quadratics with irrational (numpy) coefficients

print("\nTest 2.1: Calc finite integer iter with default threshold")
print(" Test params: cplx_x=0, cplx_y=1.75, max_iter=100")
test_iter = mands.calc_iter_int(0, 1.75, 100)
print(f"   Iter: {test_iter} (should be 3)")

print("\nTest 2.2: Calc integer iter that hits max iter with default threshold")
print(" Test params: cplx_x=0.1, cplx_y=0.1, max_iter=1000")
test_iter = mands.calc_iter_int(0.1, 0.1, 1000)
print(f"   Iter: {test_iter} (should be 1000)")




