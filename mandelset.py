# mandelset.py
#---------------
# Classes
#   MSet

DEBUG_FLAG = True

import mandelmaths as mands
import display
# import quadratics as quads

# PythonAnywhere requires Agg (not Tkinter) for backend plot generation
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import math
import sympy

class MSet(object):

    def __init__(self,frc_ctr_x=-0.5, frc_ctr_y=0.0, mag=1.0, maxiter=50, scr_width=40, scr_height=30, alg=0, pal=0, thresh=4, generations=4):

        # Take px width/height and center/mag params
        self.frc_ctr_x = frc_ctr_x
        self.frc_ctr_y = frc_ctr_y
        self.mag = mag
        self.maxiter = maxiter
        self.scr_width = scr_width
        self.scr_height = scr_height
        self.alg = alg                  # calculation algorithm 0=int, 1=dec
        self.pal = pal                  # palette
        self.thresh = 4                 # escape-time threshold
        self.generations = generations  # iterations of new approach UNUSED

        self.frc_min_x = 0.0
        self.frc_max_x = 0.0
        self.frc_min_y = 0.0
        self.frc_max_y = 0.0

        self.min_z = 999999
        self.max_z = -1

        # globals
        self._gen = 0
        self._points = {}
        self._iter_array = []
        self._pixels = []


    def calc_simple_2D_array(self, max_iter=50):
        if DEBUG_FLAG:
            print(f"Entered calc_simple_2D_array(max_iter={max_iter})...")

        img_width = self.scr_width  # for now...
        img_height = self.scr_height

        # calculate size of pixel in fractal-space (100dpu)
        # at mag 1.0, 1.0 in fractal space is 100 pixels
        # mag 2.0 --> 1.0 in fractal space is 200 pixels
        # mag 4.0 --> 1.0 in fractal space is 400 pixels
        pixel_size = 1 / (self.mag * 100)

        # calculate the corners off the center and dot_size
        frc_min_x = self.frc_ctr_x - (pixel_size * (img_width / 2))
        frc_max_x = self.frc_ctr_x + (pixel_size * (img_width / 2))
        frc_min_y = self.frc_ctr_y - (pixel_size * (img_height / 2))
        frc_max_y = self.frc_ctr_y + (pixel_size * (img_height / 2))
        if DEBUG_FLAG:
            print(f"Fractal space corners calculated based on 1 pixel = {pixel_size}...")
            print(f"   Top left    : ({frc_min_x}, {frc_max_y})")
            print(f"   Bottom right: ({frc_max_x}, {frc_min_y})")

        self._iter_array = []
        for image_y in range(img_height):
            fractal_y = frc_min_y + (pixel_size * image_y)
            for i in range(img_width):

                if i==0:  # i = 0 is the leftmost pixel in the row
                    image_x = 0
                    fractal_x = frc_min_x
                    px = Pixel(image_x, image_y, fractal_x, fractal_y)
                    px.output_z = self.calc_escape(px, self.maxiter)
                    px.output_method = "esc"
                    self._pixels.append(px)
                elif i==1:  # i = 1 is the rightmost pixel in the row
                    image_x = img_width-1
                    fractal_x = frc_min_x + (pixel_size * image_x)
                    px = Pixel(image_x, image_y, fractal_x, fractal_y)
                    px.output_z = self.calc_escape(px, self.maxiter)
                    px.output_method = "esc"
                    self._pixels.append(px)
                elif i==2:  # i = 2 is the first middle pixels in the row
                    image_x = (img_width-1) / 2
                    fractal_x = frc_min_x + (pixel_size * image_x)
                    px = Pixel(image_x, image_y, fractal_x, fractal_y)
                    px.output_z = self.calc_escape(px, self.maxiter)
                    px.output_method = "esc"
                    px.triplet_name = "T"
                    px.triplet_quat_fmla = self.generate_triplet_quat_fmla(self._pixels[0], px, self._pixels[1])
                    self._pixels.append(px)
                else:  # i > 2 are defined recursively
                    self.define_pixels_recursively(self._pixels[2], 0)
        # DEBUG
        if DEBUG_FLAG:
            for i in range(img_width):
                print(f"Name: {self._pixels[i].triplet_name}, image_x: {self._pixels[i].image_x}")


    def define_pixels_recursively(self, px_parent, px_grandparent_image_x):
        if px_parent.image_x %2 == 0:  # further subdivision is possible

            # define the pixel to the left of the parent
            left_image_x = px_parent.image_x - (abs(px_grandparent_image_x - px_parent.image_x) / 2)
            left_fractal_x = px_parent.fractal_x - (
                    px_parent.fractal_x / (2 * len(px_parent.triplet_name)))
            px_left = Pixel(left_image_x, px_parent.image_y, left_fractal_x, px_parent.fractal_y)
            px_left.triplet_name = ''.join([px_parent.triplet_name, 'L'])
            self._pixels.append(px_left)
            self.define_pixels_recursively(px_left, px_parent.image_x)

            # define the pixel to the right of the parent
            right_image_x = px_parent.image_x + (abs(px_grandparent_image_x - px_parent.image_x) / 2)
            right_fractal_x = px_parent.fractal_x + (
                    px_parent.fractal_x / (2 * len(px_parent.triplet_name)))
            px_right = Pixel(right_image_x, px_parent.image_y, right_fractal_x, px_parent.fractal_y)
            px_right.triplet_name = ''.join([px_parent.triplet_name, 'R'])
            self._pixels.append(px_right)
            self.define_pixels_recursively(px_right, px_parent.image_x)

        else:  # further subdivision is not possible
            return

    # if px.output_z < self.min_z:
    #     self.min_z = px.output_z
    # if px.output_z > self.max_z:
    #     self.max_z = px.output_z
    # self._pixels.append(px)

    # def calc(self, max_iter=20, alg='int', color='bw', thresh=4):
    #     if DEBUG_FLAG:
    #         print(f"Entered calc(alg='{alg}', max_iter={max_iter}, thresh={thresh})...")
    #
    #     self._points = []
    #     min_i = 999999
    #     max_i = -1
    #
    #     # calculate size of square 'dot'
    #     # at mag 1.0, the smaller of the screen dims is exactly 1.0 in fractal space
    #     # mag 2.0 --> 0.5 in fractal space
    #     # mag 4.0 --> 0.25
    #     narrow_dim = -1
    #     if (self.scr_width >= self.scr_height):
    #         narrow_dim = self.scr_height
    #     else:
    #         narrow_dim = self.scr_width
    #     dot_size = 1 / ((self.mag / 2) * narrow_dim)
    #
    #     # calculate the corners off the center and dot_size
    #     self.frc_min_x = self.frc_ctr_x - (dot_size * (self.scr_width / 2))
    #     self.frc_max_x = self.frc_ctr_x + (dot_size * (self.scr_width / 2))
    #     self.frc_min_y = self.frc_ctr_y - (dot_size * (self.scr_height / 2))
    #     self.frc_max_y = self.frc_ctr_y + (dot_size * (self.scr_height / 2))
    #
    #     for x in range(self.scr_width):
    #         for y in range(self.scr_height):
    #             if DEBUG_FLAG:
    #                 print("X: {}, Y: {}".format(x,y))
    #             p = Point(self.frc_min_x + (dot_size * x), self.frc_min_y + (dot_size * y))
    #
    #             p.i = mands.calc_iter(p.x, p.y, max_iter, self.alg, self.thresh)
    #
    #             #----- TEST and CONTINUE
    #             if p.i < min_i:
    #                 min_i = p.i
    #             if p.i > max_i:
    #                 max_i = p.i
    #             self._points.append(p)
    #
    #     if DEBUG_FLAG:
    #         print("During calc, found min_i: {}, max_i: {}".format(min_i, max_i))
    #     for p in self._points:
    #         p.color = mands.calc_color(p, 'bw', min_i, max_i)
    #         if DEBUG_FLAG:
    #             print("Got color for x: {}, y: {}, i: {}: {}".format(p.x, p.y, p.i, p.color))

    def calc_escape(self, pixel, max_iter):
        threshold = 4
        iter = 0
        z = complex(0, 0)
        c = complex(pixel.fractal_x, pixel.fractal_y)
        while iter < max_iter:
            iter += 1
            z = (z * z) + c
            # if (abs(z.real) > threshold) or (abs(z.imag) > threshold):
            if (abs(math.sqrt(math.pow(z.real, 2) + math.pow(z.imag, 2))) > threshold):
                break
        if True:  # calculate decimal portion
            iter_real = 0.0 + iter
            thresh_half = threshold / 2
            if iter < max_iter:
                log_zn = math.log(z.real * z.real + z.imag * z.imag) / (thresh_half)
                nu = math.log(log_zn / math.log(thresh_half)) / math.log(thresh_half)
                iter_real = iter_real + 1 - nu
            iter = iter_real
        return iter

    import sympy

    def generate_triplet_quat_fmla(self, px_left, px_mid, px_right):
        """Given three points, solve for their quadratic curve, then
            use the quadratic's coefficients to generate the fmla.
        Returns: Callable formula that takes an x and returns the height
            of the quadratic curve (y) at that x.
        """
        # Extract the x/y values
        a_x = px_left.fractal_x
        a_y = px_left.output_z
        b_x = px_mid.fractal_x
        b_y = px_mid.output_z
        c_x = px_right.fractal_x
        c_y = px_right.output_z

        # Use sympy to solve the system of equations
        a, b, c = sympy.symbols("a b c", real=True)
        eq1 = sympy.Eq(a * a_x ** 2 + b * a_x + c, a_y)
        eq2 = sympy.Eq(a * b_x ** 2 + b * b_x + c, b_y)
        eq3 = sympy.Eq(a * c_x ** 2 + b * c_x + c, c_y)
        sols = sympy.solve([eq1, eq2, eq3], [a, b, c])

        def quat_fmla(test_x):
            y = sympy.symbols("y", real=True)
            eq1 = sympy.Eq(sols[a] * test_x ** 2 + sols[b] * test_x + sols[c], y)
            sol = sympy.solve([eq1], [y])
            return sol[y]

        return quat_fmla

    #----

    def plot(self):
        if DEBUG_FLAG:
            print(f"Starting plot of {len(self._points)} points...")
        fig = plt.figure()
        ax = fig.add_subplot(111)
        for p in self._points:
            ax.plot(p.x, p.y, "ro", color=p.color, markersize=2.0)
        fig.savefig("output_imgs\graph001.png")

    def plot_PIL(self):
        if DEBUG_FLAG:
            print(f"Starting PIL plot of {len(self._iter_array)} iteration values, with")
            print(f"   min iter val: {self.min_iter}")
            print(f"   max iter val: {self.max_iter}")
        display.display_iter_array(self._iter_array, self.min_iter, self.max_iter, self.scr_width, self.scr_height)

class Pixel(object):

    def __init__(self, image_x, image_y, fractal_x, fractal_y, triplet_name=None, triplet_quat_fmla=None,
                 escape_z=None, fmla_z=None, z_diff_pct=None, output_z=None, output_method=None):
        self.image_x = image_x
        self.image_y = image_y
        self.fractal_x = fractal_x
        self.fractal_y = fractal_y
        self.triplet_name = triplet_name
        self.triplet_quat_fmla = triplet_quat_fmla
        self.escape_z = escape_z
        self.fmla_z = fmla_z
        self.z_diff_pct = z_diff_pct
        self.output_z = output_z
        self.output_method = output_method

class Point(object):
    # older; unused
    def __init__(self, x, y, i=-1, color="#000000", pid=-1, gen=-1, nu=0, nr=0, nd=0, nl=0):
        self.x = x
        self.y = y
        self.i = i
        self.color = color
        self.pid = pid
        self.gen = gen
        self.neighs = {}
        self.neighs["up"] = nu
        self.neighs["right"] = nr
        self.neighs["down"] = nd
        self.neighs["left"] = nl
        self.neigh_lox = {}
        self.neigh_lox["up"] = False
        self.neigh_lox["right"] = False
        self.neigh_lox["down"] = False
        self.neigh_lox["left"] = False

