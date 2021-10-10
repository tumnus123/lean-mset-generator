# mandelset.py
#---------------
# Last update: 10/9/2021
#              No real updates since 8/21; need to implement asyncio
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

    def __init__(self, frc_ctr_x=-0.5, frc_ctr_y=0.0, mag=1.0, maxiter=50, img_width=40, img_height=30, alg=0, pal=0, thresh=4, generations=4):

        # Take px width/height and center/mag params
        self.frc_ctr_x = frc_ctr_x
        self.frc_ctr_y = frc_ctr_y
        self.mag = mag
        self.maxiter = maxiter
        self.img_width = img_width
        self.img_height = img_height
        self.alg = alg                  # calculation algorithm 0=int, 1=dec
        self.pal = pal                  # palette
        self.thresh = 4                 # escape-time threshold

        self.frc_min_x = 0.0
        self.frc_max_x = 0.0
        self.frc_min_y = 0.0
        self.frc_max_y = 0.0
        self.pixel_size = 999999

        self.min_z = 999999
        self.max_z = -1

        # globals
        self._pixels = [None for i in range(self.img_width * self.img_height)]


    def calc_simple_2D_array(self, max_iter=50):
        if DEBUG_FLAG:
            print(f"Entered calc_simple_2D_array(max_iter={max_iter})...")

        # calculate size of pixel in fractal-space (100dpu)
        # at mag 1.0, 1.0 in fractal space is 100 pixels
        # mag 2.0 --> 1.0 in fractal space is 200 pixels
        # mag 4.0 --> 1.0 in fractal space i
        # TODO: this needs work...
        self.pixel_size = 1 / (self.mag * 10)

        # calculate the corners off the center and dot_size
        self.frc_min_x = self.frc_ctr_x - (self.pixel_size * (self.img_width / 2))
        self.frc_max_x = self.frc_ctr_x + (self.pixel_size * (self.img_width / 2))
        self.frc_min_y = self.frc_ctr_y - (self.pixel_size * (self.img_height / 2))
        self.frc_max_y = self.frc_ctr_y + (self.pixel_size * (self.img_height / 2))
        if DEBUG_FLAG:
            print(f"Fractal space corners calculated based on 1 pixel = {self.pixel_size}...")
            print(f"   Top left    : ({self.frc_min_x}, {self.frc_max_y})")
            print(f"   Bottom right: ({self.frc_max_x}, {self.frc_min_y})")

        for image_y in range(self.img_height):

            if DEBUG_FLAG:
                if image_y % 10 == 0: print(f"Processing row {image_y}")

            fractal_y = self.frc_min_y + (self.pixel_size * image_y)

            # define the leftmost pixel in the row
            image_x = 0
            fractal_x = self.frc_min_x
            px_leftmost = Pixel(image_x, image_y, fractal_x, fractal_y)
            px_leftmost.output_z = self.calc_escape(px_leftmost, self.maxiter)
            px_leftmost.output_method = "esc"
            px_leftmost.triplet_name = "L"
            self._pixels[int(self.img_width * image_y)] = px_leftmost

            # define the rightmost pixel in the row
            image_x = self.img_width-1
            fractal_x = self.frc_min_x + (self.pixel_size * image_x)
            px_rightmost = Pixel(image_x, image_y, fractal_x, fractal_y)
            px_rightmost.output_z = self.calc_escape(px_rightmost, self.maxiter)
            px_rightmost.output_method = "esc"
            px_rightmost.triplet_name = "R"
            self._pixels[int((self.img_width * (image_y + 1)) - 1)] = px_rightmost

            # define the first middle pixel in the row
            image_x = int((self.img_width-1) / 2)
            fractal_x = self.frc_min_x + (self.pixel_size * image_x)
            px_middle = Pixel(image_x, image_y, fractal_x, fractal_y)
            px_middle.output_z = self.calc_escape(px_middle, self.maxiter)
            px_middle.output_method = "esc"
            px_middle.triplet_name = "T"
            px_middle.sib_left_image_x = px_leftmost.image_x
            px_middle.sib_right_image_x = px_rightmost.image_x
            # px_middle.triplet_quat_fmla = self.generate_triplet_quat_fmla(px_leftmost, px_middle, px_rightmost)
            # self._quat_fmlas[px_middle.triplet_name] = self.bind_quat_fmla_1(px_leftmost, px_middle, px_rightmost)
            # ========================
            # Instead of storing the fmlas, store the coeffs with each pixel, and then call the solver with the coeffs
            px_middle.coeffs_list = self.get_coeffs(px_leftmost, px_middle, px_rightmost)
            self._pixels[(self.img_width * image_y) + image_x] = px_middle

            # define the remaining pixels in the row recursively
            faux_px_grandparent = self._pixels[0]
            # faux_px_grandparent.image_x = 0
            self.define_pixels_recursively(px_middle, faux_px_grandparent)

        # determine the min and max z values in the pixel array
        #
        # DEBUG: In some cases, px is type NoneType -- why? Is the array initialized with None?
        # For now, putting a condition...
        for px in self._pixels:
            if px is not None:
                if px.output_z > self.max_z: self.max_z = px.output_z
                if px.output_z < self.min_z: self.min_z = px.output_z

        # DEBUG
        # if DEBUG_FLAG:
        #     for i in range(self.img_width):
        #         # print(self._pixels[i])
        #         print(f"Name: {self._pixels[i].triplet_name}, image_x: {self._pixels[i].image_x}")


    def define_pixels_recursively(self, px_parent, px_grandparent):
        if px_parent.image_x %2 == 0:  # further subdivision is possible

            # define the pixel to the left of the parent
            left_image_x = int(px_parent.image_x - (abs(px_grandparent.image_x - px_parent.image_x) / 2))
            left_fractal_x = self.frc_min_x + (self.pixel_size * left_image_x)
            px_left = Pixel(left_image_x, px_parent.image_y, left_fractal_x, px_parent.fractal_y)
            px_left.triplet_name = ''.join([px_parent.triplet_name, 'L'])
            px_left.sib_right_image_x = px_parent.image_x
            px_left.sib_left_image_x = px_parent.sib_left_image_x
            if px_parent.output_method == "fmla":
                # we're safe to use the parent's fmla
                if DEBUG_FLAG: print(f"While processing {px_left.triplet_name}, found that it's parent used fmla output method.")
                px_left.output_z = self.calc_quat(px_parent.coeffs_list[0], px_parent.coeffs_list[1], px_parent.coeffs_list[2], left_fractal_x)
                px_left.output_method = "fmla"
                px_left.coeffs_list = px_parent.coeffs_list
            else:
                # going to need to calc escape-time for this pixel
                if DEBUG_FLAG: print(f"While processing {px_left.triplet_name}, found that it needed escape-time calculated.")
                px_left.escape_z = self.calc_escape(px_left, self.maxiter)
                # now use the parent's coeffs to calc this pixel's fmla_z and compare the result with its escape-time
                if DEBUG_FLAG: print(f"Parent {px_parent.triplet_name} coeffs list len is {len(px_parent.coeffs_list)}")
                px_left_parent_fmla_z = self.calc_quat(px_parent.coeffs_list[0],
                                                       px_parent.coeffs_list[1],
                                                       px_parent.coeffs_list[2], left_fractal_x)
                if DEBUG_FLAG: print(f"   {px_left.triplet_name} escape z: {px_left.escape_z}")
                if DEBUG_FLAG: print(f"   versus {px_parent.triplet_name} fmla z: {px_left_parent_fmla_z}")
                px_left_z_diff_parent = (abs(px_left.escape_z - px_left_parent_fmla_z) / px_left.escape_z) * 100
                if px_left_z_diff_parent < 1.0:
                    # use the grandparent's coeffs to calc this pixel's fmla_z and compare the result with its escape-time
                    px_left_grandparent_fmla_z = self.calc_quat(px_parent.coeffs_list, left_fractal_x)
                    px_left_z_diff_grandparent = (abs(px_left.escape_z - px_left_grandparent_fmla_z) / px_left.escape_z) * 100
                    if px_left_z_diff_grandparent < 1.0:
                        # we're safe to use the parent's fmla
                        px_left.output_z = px_left_parent_fmla_z
                        px_left.output_method = "fmla"
                        px_left.coeffs_list = px_parent.coeffs_list
                    else:
                        # we're going to use this pixel's escape-time
                        px_left.output_z = px_left.escape_z
                        px_left.output_method = "esc"
                        # calc this pixel's coefficients so the next iteration can use them for testing
                        px_parent_sib_left_index = px_parent.sib_left_image_x
                        if DEBUG_FLAG: print(f"Parent's sib left image x is {px_parent_sib_left_index}")
                        px_parent_sib_left = self._pixels[px_parent_sib_left_index]
                        if DEBUG_FLAG: print(f"Parent's sib left is {px_parent_sib_left}")
                        px_left.coeffs_list = self.get_coeffs(px_parent_sib_left, px_left, px_parent)
            self._pixels[(self.img_width * px_parent.image_y) + left_image_x] = px_left

            # define the pixel to the right of the parent
            right_image_x = int(px_parent.image_x + (abs(px_grandparent.image_x - px_parent.image_x) / 2))
            right_fractal_x = self.frc_min_x + (self.pixel_size * right_image_x)
            px_right = Pixel(right_image_x, px_parent.image_y, right_fractal_x, px_parent.fractal_y)
            px_right.triplet_name = ''.join([px_parent.triplet_name, 'R'])
            px_right.sib_right_image_x = px_parent.image_x
            px_right.sib_right_image_x = px_parent.sib_right_image_x
            if px_parent.output_method == "fmla":
                # we're safe to use the parent's fmla
                px_right.output_z = self.calc_quat(px_parent.coeffs_list, right_fractal_x)
                px_right.output_method = "fmla"
                px_right.coeffs_list = px_parent.coeffs_list
            else:
                # going to need to calc escape-time for this pixel
                px_right.escape_z = self.calc_escape(px_right, self.maxiter)
                # now use the parent's coeffs to calc this pixel's fmla_z and compare the result with its escape-time
                px_right_parent_fmla_z = self.calc_quat(px_parent.coeffs_list[0],
                                                        px_parent.coeffs_list[1],
                                                        px_parent.coeffs_list[2], right_fractal_x)
                px_right_z_diff_parent = (abs(px_right.escape_z - px_right_parent_fmla_z) / px_right.escape_z) * 100
                if px_right_z_diff_parent < 1.0:
                    # use the grandparent's coeffs to calc this pixel's fmla_z and compare the result with its escape-time
                    px_right_grandparent_fmla_z = self.calc_quat(px_parent.coeffs_list, right_fractal_x)
                    px_right_z_diff_grandparent = (abs(px_right.escape_z - px_right_grandparent_fmla_z) / px_right.escape_z) * 100
                    if px_right_z_diff_grandparent < 1.0:
                        # we're safe to use the parent's fmla
                        px_right.output_z = px_right_parent_fmla_z
                        px_right.output_method = "fmla"
                        px_right.coeffs_list = px_parent.coeffs_list
                    else:
                        # we're going to use this pixel's escape-time
                        px_right.output_z = px_right.escape_z
                        px_right.output_method = "esc"
                        # calc this pixel's coefficients so the next iteration can use them for testing
                        px_parent_sib_right_index = px_parent.sib_right_image_x
                        if DEBUG_FLAG: print(f"Parent's sib right image x is {px_parent_sib_right_index}")
                        px_parent_sib_right = self._pixels[px_parent_sib_right_index]
                        if DEBUG_FLAG: print(f"Parent's sib left is {px_parent_sib_left}")
                        px_right.coeffs_list = self.get_coeffs(px_parent, px_right, px_parent_sib_right)
            self._pixels[(self.img_width * px_parent.image_y) + right_image_x] = px_right

            # recursively define the next generation of pixels
            self.define_pixels_recursively(px_left, px_parent)
            self.define_pixels_recursively(px_right, px_parent)


        else:  # further subdivision is not possible
            return

    def calc_escape(self, px, max_iter):
        threshold = 4
        iter = 0
        z = complex(0, 0)
        c = complex(px.fractal_x, px.fractal_y)
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

    def calc_quat(self, a, b, c, fractal_x):
        if DEBUG_FLAG:
            print(a, b, c)
        y = sympy.symbols("y", real=True)
        eq = sympy.Eq(a * fractal_x ** 2 + b * fractal_x + c, y)
        sol = sympy.solve([eq], [y])
        return sol[y]


    def get_coeffs(self, px_left, px_mid, px_right):
        # Extract the x/y values
        a_x = px_left.fractal_x
        a_y = px_left.output_z
        b_x = px_mid.fractal_x
        b_y = px_mid.output_z
        c_x = px_right.fractal_x
        c_y = px_right.output_z
        # TEMP DEBUG
        print(f"ax({px_left.triplet_name}): {a_x}, ay:: {a_y}, bx({px_mid.triplet_name}): {b_x}, by: {b_y}, cx({px_right.triplet_name}): {c_x}, cy: {c_y}")

        # Use sympy to solve the system of equations
        a, b, c = sympy.symbols("a b c", real=True)
        eq1 = sympy.Eq(a * a_x ** 2 + b * a_x + c, a_y)
        eq2 = sympy.Eq(a * b_x ** 2 + b * b_x + c, b_y)
        eq3 = sympy.Eq(a * c_x ** 2 + b * c_x + c, c_y)
        sols = sympy.solve([eq1, eq2, eq3], [a, b, c])

        return [sols[a], sols[b], sols[c]]



    #----

    def plot_PIL(self):
        if DEBUG_FLAG:
            print(f"Starting PIL plot of {len(self._pixels)} iteration values, with")
            print(f"   min z: {self.min_z}")
            print(f"   max z: {self.max_z}")
        display.display_iter_array(self._pixels, self.min_z, self.max_z, self.img_width, self.img_height)

class Pixel(object):

    def __init__(self, image_x, image_y, fractal_x, fractal_y, triplet_name=None, sib_left_image_x=None, sib_right_image_x=None, triplet_quat_fmla=None,
                 escape_z=None, fmla_z=None, z_diff_pct=99.99, output_z=None, output_method=None):
        self.image_x = image_x
        self.image_y = image_y
        self.fractal_x = fractal_x
        self.fractal_y = fractal_y
        self.triplet_name = triplet_name
        self.sib_left_image_x = sib_left_image_x
        self.sib_right_image_x = sib_right_image_x
        self.coeffs_list = []
        self.escape_z = escape_z
        self.fmla_z = fmla_z
        self.z_diff_pct = z_diff_pct
        self.output_z = output_z
        self.output_method = output_method
