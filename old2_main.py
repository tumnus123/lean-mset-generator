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

    # =========================================================================
    # =========================================================================
    # =========================================================================
    def generate_subsegments(self, line, num_pieces):
        """Given a line (ordered list of 2+ Points), generate subsegments."""

        # inner functions
        def get_segments(a_line):
            line_segments = []
            i = 0
            while i < len(a_line)-1:
                line_segments.append([a_line[i], a_line[i+1]])
                i += 1

            return line_segments

        def split_segment(seg, num_pieces):
            p1 = seg[0]
            p2 = seg[1]
            print(f"Splitting segment: {p1.x},{p1.y}\t{p2.x},{p2.y}")
            # calc delta x and delta y
            delta_x = p2.x - p1.x
            delta_y = p2.y - p1.y
            x_array = []
            y_array = []
            dist_x = delta_x / num_pieces
            dist_y = delta_y / num_pieces
            for i in range(num_pieces-1):
                x_array.append(p1.x + ((i+1)*dist_x))
                y_array.append(p1.y + ((i+1)*dist_y))

            pt_array = [p1]
            for i in range(num_pieces-1):
                new_pt = Point(x_array[i], y_array[i], 0, 0)
                pt_array.append(new_pt)
            pt_array.append(p2)

            # debug
            print("split_line points:")
            for p in pt_array:
                print(f"\t\t\t{p.x},{p.y}")

            return pt_array

        # main
        print(f"Starting main...")
        segments = get_segments(line)
        print(f"Got {len(segments)} line segments.")
        split_pts = []
        out_line = []
        for seg in segments:
            split_pts = split_segment(seg, num_pieces)
            del split_pts[len(split_pts)-1] # trim last pt to avoid dupes
            for p in split_pts:
                out_line.append(p)
        out_line.append(line[len(line)-1]) # untrim the very last pt

        print(f"Points in out_line:")
        for i in range(len(out_line)):
            p = out_line[i]
            if type(p) is list:
                for j in range(len(p)):
                    print(f"\tList {j}:\t{p[j].x},{p[j].y}")
            else:
                print(f"\tPt {i}:\t{p.x},{p.y}")
            #for j in range(len(seg)):
            #print(f"\tPoint {i}:\t{p.x},{p.y}")

        return out_line


    def generate_lean_old(self):
        # establish corner points
        p_ll = Point(self.xmin,self.ymin,3,0, 1,4,-1,-1)
        p_lr = Point(self.xmax,self.ymin,4,0, 2,-1,-1,3)
        p_ul = Point(self.xmin,self.ymax,1,0, -1,2,3,-1)
        p_ur = Point(self.xmax,self.ymax,2,0, -1,-1,4,1)
        p_arr = [p_ul,p_ur,p_ll,p_lr]
        for p in p_arr:
            p.i = self.calc_smooth(p, 100)
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
        # print(self._points)
        fig = plt.figure()
        ax = fig.add_subplot(111)
        for p in self._points:
            ax.plot(p.x, p.y, "ro", color=p.color, markersize=2.5)
        fig.savefig("graph001.png")


    def generate_full(self, dots_x=20, dots_y=20):
        # makes a "standard" graph of the mset
        # used for testing and calibration purposes

        self._points = []
        min_i = 999999
        max_i = -1
        x_delta = (self.xmax - self.xmin) / dots_x
        y_delta = (self.ymax - self.ymin) / dots_y

        for x in range(dots_x):
            for y in range(dots_y):
                # print("X: {}, Y: {}".format(x,y))
                p = Point(self.xmin + (x_delta * x), self.ymin + (y_delta * y))
                p.i = self.calc_smooth(p, 100)
                if p.i < min_i:
                    min_i = p.i
                if p.i > max_i:
                    max_i = p.i
                self._points.append(p)

        print("min_i: {}, max_i: {}".format(min_i, max_i))
        for p in self._points:
            # print("x: {}, y: {}, i: {}".format(p.x, p.y, p.i))
            p.color = self.get_color(p, min_i, max_i)


    def get_color(self, p, min_i, max_i):
        # normalize iter range over 0-255
        norm_i = int(((p.i - min_i) / (max_i - min_i)) * 255)

        # apply normalized iter to color (hex)
        #return([norm_i,0,0])
        hex_str = '#%02x%02x%02x' % (255-norm_i, 255-norm_i, 255-norm_i)
        print(hex_str)
        return(hex_str)





print("-----")
mset = MSet(-1.5, -1.2, 0.5, 1.2, 20)
#mset.generate_full()
#mset.report()
#mset.plot()

print("Test 1: Split flat single-segment line into flat two-segment line")
t1_p0 = Point(-1.0,0.8)
t1_p1 = Point(0.0,0.8)
t1_p2 = Point(1.0,0.8)
test_line = [t1_p0, t1_p2]
result = mset.generate_subsegments(test_line, 2)
assert result[0] is t1_p0, "T1: First point is wrong."
assert result[1].x == t1_p1.x, "T1: Middle point x is wrong."
assert result[1].y == t1_p1.y, "T1: Middle point y is wrong."
assert result[2] is t1_p2, "T1: Last point is wrong."

print("Test 2: Split flat single-segment line into flat 4-segment line")
t2_p0 = Point(-1.0,0.8)
t2_p1 = Point(-0.5,0.8)
t2_p3 = Point(0.5,0.8)
t2_p4 = Point(1.0,0.8)
test_line = [t2_p0, t2_p4]
result = mset.generate_subsegments(test_line, 4)
assert result[0] is t2_p0, "T2: First point is wrong."
assert result[1].x == t2_p1.x, "T2: P1 x is wrong."
assert result[3].x == t2_p3.x, "T2: P3 y is wrong."
assert result[4] is t2_p4, "T2: Last point is wrong."

print("Test 3: Split sloped single-segment line into two segments")
t3_p0 = Point(-1.0,-0.8)
t3_p1 = Point(0.0,0.0)
t3_p2 = Point(1.0,0.8)
test_line = [t3_p0, t3_p2]
result = mset.generate_subsegments(test_line, 2)
assert result[0] is t3_p0, "T3: First point is wrong."
assert result[1].x == t3_p1.x, "T3: Middle point x is wrong."
assert result[1].y == t3_p1.y, "T3: Middle point y is wrong."
assert result[2] is t3_p2, "T3: Last point is wrong."

print("Test 4: Split two-segment line into line with four segments")
t4_p0 = Point(-1.0,0.8)
t4_p1 = Point(-0.5,0.8)
t4_p2 = Point(0.0,0.8)
t4_p3 = Point(0.5,0.8)
t4_p4 = Point(1.0,0.8)
test_line = [t4_p0, t4_p2, t4_p4]
result = mset.generate_subsegments(test_line, 2)
assert result[0] is t4_p0, "T4: First point is wrong."
assert result[1].x == t4_p1.x, "T4: P1 x is wrong."
assert result[2] is t4_p2, "T4: Mid-point is wrong."
assert result[3].x == t4_p3.x, "T4: P3 x is wrong."
assert result[4] is t4_p4, "T4: Last point is wrong."
