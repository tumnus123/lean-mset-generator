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

class MSet(object):

    def __init__(self,frc_ctr_x=-0.5, frc_ctr_y=0.0, mag=1.0, scr_width=40, scr_height=30, alg=0, pal=0, thresh=4, generations=4):

        # Take px width/height and center/mag params
        self.frc_ctr_x = frc_ctr_x
        self.frc_ctr_y = frc_ctr_y
        self.mag = mag
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

        self.min_iter = 999999
        self.max_iter = -1

        # globals
        self._gen = 0
        self._points = {}
        self._iter_array = []


    def calc_simple_2D_array(self, max_iter=50):
        if DEBUG_FLAG:
            print(f"Entered calc_simple_2D_array(max_iter={max_iter})...")

        img_width = self.scr_width  # for now...
        img_height = self.scr_height

        # calculate size of pixel in fractal-space
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
        for y in range(img_height):
            for x in range(img_width):
                this_iter = mands.calc_iter(frc_min_x + (pixel_size * x), frc_min_y + (pixel_size * y), max_iter, self.alg, self.thresh)

                if this_iter < self.min_iter:
                    self.min_iter = this_iter
                if this_iter > self.max_iter:
                    self.max_iter = this_iter
                self._iter_array.append(this_iter)


    def calc(self, max_iter=20, alg='int', color='bw', thresh=4):
        if DEBUG_FLAG:
            print(f"Entered calc(alg='{alg}', max_iter={max_iter}, thresh={thresh})...")

        self._points = []
        min_i = 999999
        max_i = -1

        # calculate size of square 'dot'
        # at mag 1.0, the smaller of the screen dims is exactly 1.0 in fractal space
        # mag 2.0 --> 0.5 in fractal space
        # mag 4.0 --> 0.25
        narrow_dim = -1
        if (self.scr_width >= self.scr_height):
            narrow_dim = self.scr_height
        else:
            narrow_dim = self.scr_width
        dot_size = 1 / ((self.mag / 2) * narrow_dim)

        # calculate the corners off the center and dot_size
        self.frc_min_x = self.frc_ctr_x - (dot_size * (self.scr_width / 2))
        self.frc_max_x = self.frc_ctr_x + (dot_size * (self.scr_width / 2))
        self.frc_min_y = self.frc_ctr_y - (dot_size * (self.scr_height / 2))
        self.frc_max_y = self.frc_ctr_y + (dot_size * (self.scr_height / 2))

        for x in range(self.scr_width):
            for y in range(self.scr_height):
                if DEBUG_FLAG:
                    print("X: {}, Y: {}".format(x,y))
                p = Point(self.frc_min_x + (dot_size * x), self.frc_min_y + (dot_size * y))

                p.i = mands.calc_iter(p.x, p.y, max_iter, self.alg, self.thresh)

                #----- TEST and CONTINUE
                if p.i < min_i:
                    min_i = p.i
                if p.i > max_i:
                    max_i = p.i
                self._points.append(p)

        if DEBUG_FLAG:
            print("During calc, found min_i: {}, max_i: {}".format(min_i, max_i))
        for p in self._points:
            p.color = mands.calc_color(p, 'bw', min_i, max_i)
            if DEBUG_FLAG:
                print("Got color for x: {}, y: {}, i: {}: {}".format(p.x, p.y, p.i, p.color))

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

class Point(object):

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

