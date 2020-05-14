# lean-mset-generator
Trying a new (AFAIK) lean geometry approach to Mandelbrot set generation.

The concept: Test points in an increasingly finer grid. Keep track of each point's nearest neignbors. 
Calculate the curve formed by adjacent points' z-values. Use the curve to predict the z values of 
points that will be calculated in the next finer grid of points. If the predicted z value is within
some tolerance of the calculated z value, we can stop using escape-time calculations (expensive) in that area,
and instead use the curve's formula(e) (cheaper) to get approximate z-values.

The efficacy of this approach will vary. The greatest gains will be in deeper zooms with smoother areas.
