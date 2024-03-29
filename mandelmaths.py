# mandelmaths.py
#---------------
# Functions
#   calc_iter
#     Given a pair of numbers representing a point on the complex plane,
#     return the (int) number of iterations before the result exceeds some
#     threshold. If the number of iterations exceeds some maximum, return
#     the maximum. If desired, can also return decimal representing how close
#     iter was to the threshold.

import math

def calc_iter(cplx_x, cplx_y, max_iter=20, alg=0, threshold=4):
    iter = 0
    z = complex(0,0)
    c = complex(cplx_x, cplx_y)
    while iter < max_iter:
        iter += 1
        z = (z * z) + c
        # if (abs(z.real) > threshold) or (abs(z.imag) > threshold):
        if (abs(math.sqrt(math.pow(z.real,2) + math.pow(z.imag,2))) > threshold):
            break
    if alg==1: # calculate decimal portion
        iter_real = 0.0 + iter
        thresh_half = threshold / 2
        if iter < max_iter:
            log_zn = math.log(z.real*z.real + z.imag*z.imag) / (thresh_half)
            nu = math.log( log_zn / math.log(thresh_half) ) / math.log(thresh_half)
            iter_real = iter_real + 1 - nu
        iter = iter_real
    return iter



# ============

# def calc_iter_dec(pt, threshold, max_iter):
#     iter = 0
#     z = complex(0,0)
#     c = complex(pt.x, pt.y)
#     while iter < max_iter:
#         iter += 1
#         z = (z * z) + c
#         if (abs(z.real) > threshold) or (abs(z.imag) > threshold):
#             break
#     # calculate decimal portion
#     iter_real = 0.0 + iter
#     thresh_half = threshold / 2
#     if iter < max_iter:
#         log_zn = math.log(z.real*z.real + z.imag*z.imag) / (thresh_half)
#         nu = math.log( log_zn / math.log(thresh_half) ) / math.log(thresh_half)
#         iter_real = iter_real + 1 - nu
#     return iter_real
