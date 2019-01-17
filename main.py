

# divide-and-conquer

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

    def __init__(self,xmin,ymin,xmax,ymax):
        self.gen = 0
        self.extent = {
            "xmin": xmin,
            "ymin": ymin,
            "xmax": xmax,
            "ymax": ymax
        }
        # establish corner points
        self.points = {}
        p_ll = Point(xmin,ymin,3,0, 1,4,-1,-1)
        p_lr = Point(xmax,ymin,4,0, 2,-1,-1,3)
        p_ul = Point(xmin,ymax,1,0, -1,2,3,-1)
        p_ur = Point(xmax,ymax,2,0, -1,-1,4,1)
        p_arr = [p_ul,p_ur,p_ll,p_lr]
        for p in p_arr:
            p.i = self.calc_iter(p, 100)
            self.points.setdefault(p.pid, p)

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
        return len(self.points) + 1

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
        pt_c = Point(pt_c_x, pt_c_y, pt_c_id, self.gen+1)

        if self.debug_flag:
            print("Created mid pt:")
            print("   id={}, x={}, y={}, gen={}".format(pt_c.pid, pt_c.x, pt_c.y, pt_c.gen))
        return pt_c

    def update_neighs(self, pt_a, pt_b, pt_c):
        # determine easy neighs

        # determine hard neighs

        return True

    def report(self):
        print("----- begin report -----")
        print("Total points: {}".format(len(self.points)))
        for i in range(self.gen + 1):
            print("  Gen {}: nn points".format(i))
        print("----- end report -----")

    def generate(self):
        # print("sg:",self.gen)
        tot_points_to_gen = 0
        for i in self.points:
            # print("pg:",self.points[i].gen)
            if self.points[i].gen==self.gen:
                tot_points_to_gen += 1
        points_gen_count = 1
        for i in self.points:
            p = self.points[i]
            if p.gen==self.gen:

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
                        neigh = self.points[p.neighs[dir]]
                        opp_dir = self.get_opp_dir(dir)

                        neigh_locked_in_opp_dir = neigh.neigh_lox[opp_dir]
                        print("    Neigh (pid={}) locked in {} dir? {}".format(neigh.pid, opp_dir, neigh.neigh_lox[opp_dir]))
                        if not neigh_locked_in_opp_dir:
                            # if B.gen <> curr_gen, skip
                            if neigh.gen==self.gen:
                                mid_pt = self.create_mid_pt(p, neigh)
                                # cant delta dict while iterating
                                # self.points[mid_pt.pid] = mid_pt
                                mid_pt_with_neighs = self.update_neighs(p, neigh, mid_pt)
                                self.report()
                points_gen_count += 1

        # process each points
            # consider each neighbor
                # if n.pid > 0
                #    and this pair hasnt been gen'd yet
                #    and...
                #
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



mset = MSet(-0.8,-0.9,0.8,0.9)
print(mset.extent["xmin"])
print("next pid:",mset.get_next_pid())
for p in mset.points.values():
    print("id:{}, gen:{}, iters:{}".format(p.pid, p.gen, p.i))
    for n in p.neighs:
        print("   {}:{}, {}".format(n, p.neighs[n], p.neigh_lox[n]))

print("-----")
mset.generate()







