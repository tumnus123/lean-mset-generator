# lean-mset-generator
# Author: Jason Hine (tumnus123@gmail.com)
#
# Objective: A new, efficient algorithm for generating an image of the Mandelbrot
# set (or other escape-time fractals). For a given row of pixels, iteratively find
# midpoints between existing points to form "triplets". Determine quadratic coefficients
# for each triplet. Calculate one of the triplet's children (e.g., left midpoint) using both
# escape-time and quadratic equation. If results of both calculations are similar enough,
# consider using the quadratic eq to determine the remaining pixels in the triplet's range.
#

from mandelset import MSet
import asyncio
from datetime import datetime

print("Starting...")
start_time = datetime.now()
# mset = MSet(-0.18, 1.05, 15.0, 40, 30)
mset = MSet(
    frc_ctr_x=-0.18,
    frc_ctr_y=1.05,
    # frc_ctr_x=0,
    # frc_ctr_y=0,
    mag=50.0,
    img_width=65,
    img_height=49,
    alg=0,
    pal=0,
    thresh=4,
    generations=4)

# mset.calc()
asyncio.run(mset.calc_simple_2D_array())
# mset.plot()
mset.plot_PIL()

print(f"FINISHED in {datetime.now() - start_time} seconds")