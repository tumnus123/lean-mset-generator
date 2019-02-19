# lean-mset-generator
# Author: Jason Hine (tumnus123@gmail.com)
#
# Objective: A new, highly-efficient algorithm for generating the Mandelbrot
# set. Given four corners, iteratively find midpoints between existing points.
# Test midpoints against X increasingly distant neighboring points to see if
# graph of slopes follows a smooth curve. When test passes 99%, lock most distant
# lower-iter point in the test set so it is no longer a candidate for mid-point
# finding. When test passes 99.999%, calculate the limit as iters go to inf, add
# that point as being on the edge of the M-set, and lock it.
#
# The first phase will be to get the algorithm working for a single line.
#

# PythonAnywhere requires Agg (not Tkinter) for backend plot generation
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import math


class Point(object):
    pid = -1
    x = 0.0
    y = 0.0
    i = 0

    def __init__(self, x, y, pid, gen, nu=0, nr=0, nd=0, nl=0):
        self.x = x
        self.y = y
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

class MSet(object):

    debug_flag = True

    def __init__(self,xmin,ymin,xmax,ymax,maxiter):

        # parameters
        self.extent = {
            "xmin": xmin,
            "ymin": ymin,
            "xmax": xmax,
            "ymax": ymax
        }
        self.xmin = xmin
        self.xmax = xmax
        self.ymin = ymin
        self.ymax = ymax
        self.maxiter = maxiter

        # globals
        self._gen = 0
        self._points = {}

    def calc_iter(self, pt, max_iter):
        iter = 0
        z = complex(0,0)
        c = complex(pt.x, pt.y)
        while iter < max_iter:
            iter += 1
            z = (z * z) + c
            if (abs(z.real) > 4) or (abs(z.imag) > 4):
                break
        return iter

    def calc_smooth(self, pt, max_iter):
        iter = 0
        z = complex(0,0)
        c = complex(pt.x, pt.y)
        while iter < max_iter:
            iter += 1
            z = (z * z) + c
            if (abs(z.real) > 4) or (abs(z.imag) > 4):
                break
        # calculate decimal portion
        iter_real = 0.0 + iter
        if iter < max_iter:
            log_zn = math.log(z.real*z.real + z.imag*z.imag) / 2
            nu = math.log( log_zn / math.log(2) ) / math.log(2)
            iter_real = iter_real + 1 - nu
        return iter_real

    def calc_slope(self, p1, p2):
        d_x = abs(p1.x - p2.x)
        d_y = abs(p1.y - p2.y)
        run = -1
        if (d_x > d_y):
            run = d_x
        else:
            run = d_y
        rise = abs(p1.i - p2.i)
        return rise / run

    def get_next_pid(self):
        return len(self._points) + 1

    def get_opp_dir(self, d):
        opp = ""
        if d == "up":
            opp = "down"
        elif d == "down":
            opp = "up"
        elif d == "left":
            opp = "right"
        elif d == "right":
            opp = "left"
        else:
            opp = "unk"
        return opp

    def create_mid_pt(self, pt_a, pt_b):
        # considers both x and y diffs
        # subtract the smaller from the larger and add to the smaller
        pt_c_x = 0
        if pt_a.x < pt_b.x:
            pt_c_x = ((pt_b.x - pt_a.x) / 2) + pt_a.x
        else:
            pt_c_x = ((pt_a.x - pt_b.x) / 2) + pt_b.x
        pt_c_y = 0
        if pt_a.y < pt_b.y:
            pt_c_y = ((pt_b.y - pt_a.y) / 2) + pt_a.y
        else:
            pt_c_y = ((pt_a.y - pt_b.y) / 2) + pt_b.y
        pt_c_id = self.get_next_pid()
        pt_c = Point(pt_c_x, pt_c_y, pt_c_id, self._gen+1)

        if self.debug_flag:
            print("Created mid pt:")
            print("   id={}, x={}, y={}, gen={}".format(pt_c.pid, pt_c.x, pt_c.y, pt_c.gen))
        return pt_c

    def update_neighs(self, pt_a, pt_b, pt_c):
        # determine easy neighs
        print("pt_a.neighs['left'] is {}".format(pt_a.neighs["left"]))
        print("pt_b.pid is {}".format(pt_b.pid))
        print("pt_b.neighs['right'] is {}".format(pt_b.neighs["right"]))
        print("pt_a.pid is {}".format(pt_a.pid))

        if pt_a.neighs["left"] == pt_b.pid:
            pt_c.neighs["left"] = pt_b.pid
            pt_c.neighs["right"] = pt_a.pid
        elif pt_a.neighs["right"] == pt_b.pid:
            pt_c.neighs["right"] = pt_b.pid
            pt_c.neighs["left"] = pt_a.pid
        elif pt_a.neighs["up"] == pt_b.pid:
            pt_c.neighs["up"] = pt_b.pid
            pt_c.neighs["down"] = pt_a.pid
        elif pt_a.neighs["down"] == pt_b.pid:
            pt_c.neighs["down"] = pt_b.pid
            pt_c.neighs["up"] = pt_a.pid


        # TODO: determine hard neighs

        return pt_c

    def prezero(self, s, width):
        curr_width = len(s)
        while curr_width < width:
            s = "0" + s
            curr_width = len(s)
        return s

    def report(self):
        print("----- begin report -----")
        print("Total points: {}".format(len(self._points)))
        for i in range(self._gen + 1):
            print("  Gen {}: nn points".format(i))

        print("----- layout -----")
        w = 2 # width of items
        buf = ""
        while len(buf) < w:
            buf = buf + " "
        for i in self._points:
            p = self._points[i]
            n_up = str(p.neighs["up"])
            n_up = self.prezero(n_up, w)
            print("[ {} {} {} ]".format(buf, n_up, buf))
            n_l = str(p.neighs["left"])
            n_l = self.prezero(n_l, w)
            n_r = str(p.neighs["right"])
            n_r = self.prezero(n_r, w)
            p_id = str(p.pid)
            p_id = self.prezero(p_id, w)
            print("[ {} {} {} ] {}".format(n_l,p_id,n_r,p.i))
            n_dn = str(p.neighs["down"])
            n_dn = self.prezero(n_dn, w)
            print("[ {} {} {} ]".format(buf, n_dn, buf))
            print("--{}-{}-{}--".format(buf,buf,buf))
        print("----- end report -----")


    def generate_lean(self):
        # establish corner points
        p_ll = Point(self.xmin,self.ymin,3,0, 1,4,-1,-1)
        p_lr = Point(self.xmax,self.ymin,4,0, 2,-1,-1,3)
        p_ul = Point(self.xmin,self.ymax,1,0, -1,2,3,-1)
        p_ur = Point(self.xmax,self.ymax,2,0, -1,-1,4,1)
        p_arr = [p_ul,p_ur,p_ll,p_lr]
        for p in p_arr:
            p.i = self.calc_iter(p, 100)
            self._points.setdefault(p.pid, p)

        # print("sg:",self._gen)
        tot_points_to_gen = 0
        for i in self._points:
            # print("pg:",self._points[i].gen)
            if self._points[i].gen==self._gen:
                tot_points_to_gen += 1
        points_gen_count = 1
        for i in self._points:
            p = self._points[i]
            if p.gen==self._gen:

                print("Generating point {} ({} of {}):".format(p.pid, points_gen_count, tot_points_to_gen))
                for dir in p.neighs:
                    print("  Processing '{}' dir...".format(dir))
                    # If pt A's neigh id in dir d is -1,
                    #    lock pt A in dir d.
                    if p.neighs[dir] == -1:
                        p.neigh_lox[dir] = True
                        print("    Neigh is -1; now locked")
                    # If pt A is not locked in a dir,
                    # and neighbor B is not locked in the opposite dir:
                    self_locked_in_dir = p.neigh_lox[dir]
                    print("    Self (pid={}) locked in {} dir? {}".format(p.pid, dir, p.neigh_lox[dir]))
                    if not self_locked_in_dir:
                        neigh = self._points[p.neighs[dir]]
                        opp_dir = self.get_opp_dir(dir)

                        neigh_locked_in_opp_dir = neigh.neigh_lox[opp_dir]
                        print("    Neigh (pid={}) locked in {} dir? {}".format(neigh.pid, opp_dir, neigh.neigh_lox[opp_dir]))
                        if not neigh_locked_in_opp_dir:
                            # if B.gen <> curr_gen, skip
                            if neigh.gen==self._gen:
                                mid_pt = self.create_mid_pt(p, neigh)
                                # cant delta dict while iterating
                                # self._points[mid_pt.pid] = mid_pt
                                mid_pt_with_neighs = self.update_neighs(p, neigh, mid_pt)
                                # self.report()
                points_gen_count += 1

        # process each points
            # consider each neighbor
                # if n.pid > 0
                #    and this pair hasnt been gen'd yet
                #    and...
                #

    def junk_code(self):
        # curr_gen = 1
        # for each pt with gen==curr_gen:
        # for each dir d:

        # A and B,
        # Compare pt A iter to iters of neighs in dir of new neigh
        #    If at least 3 consec neigh iters are all within some f(x) of pt A iter,
        # then lock pt A in that dir.
        #
        # New point neighbor values init to 0.
        # A val of -1 is an edge

        # When a new pt C is made,
        # two neighs are already known and assigned.
        # To find the other two:
        pass

    def assign_neighbors(self, pt):
        # Look at both known neighs, A and B.
        for d in range(5):
            pass

        # Look at their perp neigh vals, a pair at a time:
        #    If both are -1, then set C's neigh in same dir = -1
        #    Else look at the id'd neighs themselves (D and E).
        #    Look in the dir of C at their neigh vals.
        #    If both are each other's id, c has no neigh in that dir yet; set to zero
        #    If both are same id, that's C's neigh in that dir
        #    Else diff id's, so look to the next further out
        #            neigh of the pt with the higher id.

    def plot(self):
        pass

    def generate_full(self, dots_x=40, dots_y=30):
        # makes a "standard" graph of the mset
        # used for testing and calibration purposes

        self._points = {}

        for x in range(dots_x):
            for y in range(dots_y):
                print("X: {}, Y: {}".format(x,y))



mset = MSet(-0.8, -0.9, 0.8, 0.9, 20)
# print(mset.extent["xmin"])
# print("next pid:",mset.get_next_pid())
# for p in mset._points.values():
#     print("id:{}, gen:{}, iters:{}".format(p.pid, p.gen, p.i))
#     for n in p.neighs:
#         print("   {}:{}, {}".format(n, p.neighs[n], p.neigh_lox[n]))

print("-----")
mset.generate_lean()
mset.report()

fig = plt.figure()
ax = fig.add_subplot(111)
ax.plot([1,2,3,4])
# fig.savefig("graph001.png")








