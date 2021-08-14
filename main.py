# lean-mset-generator
# Author: Jason Hine (tumnus123@gmail.com)
#
# Objective: A new, highly-efficient algorithm for generating the Mandelbrot
# set. Given four corners, iteratively find midpoints between existing points.
# Test midpoints against X number of increasingly distant neighboring points to see if
# graph of slopes follows a smooth curve. When test passes 99%, lock most distant
# lower-iter point in the test set so it is no longer a candidate for mid-point
# finding. When test passes 99.999%, calculate the limit as iters go to inf, add
# that point as being on the edge of the M-set, and lock it.
#
# Usage:
# MSet( frc_ctr_x=-0.5,
#       frc_ctr_y=0.0,
#       mag=1.0,
#       scr_width=40,
#       scr_height=30,
#       alg=0,
#       pal=0,
#       thresh=4,
#       generations=4)

from mandelset import MSet

print("Starting...")
mset = MSet(
    frc_ctr_x=-0.102,
    frc_ctr_y=0.96,
    mag=5.0,
    scr_width=80,
    scr_height=60,
    alg=0,
    pal=0,
    thresh=4,
    generations=4)

mset.calc()
mset.plot()

print("... Done!")