import math
import random
import numpy
from tkinter import *
import cityUI

# given properties
Lambda = 1/12           # /sec
mapEdge = 2500.0        # m
carSpeed = 20.0         # m/s
Pt = 120.0              # db
offsetVal = 100         # m
callTime = 60 * 5       # 5 min in average
releaseTime = 30 * 60   # 30 min in average
Pmin = 20               # db
entropy = 25            # db

# self define var
UP = 0
RIGHT = 3
LEFT = 2
DOWN = 1
transition = [[UP, DOWN, LEFT, RIGHT], [DOWN, UP, RIGHT, LEFT],
              [LEFT, RIGHT, DOWN, UP], [RIGHT, LEFT, UP, DOWN]]

Minimum = 0
BestEffort = 1
Entropy = 2
SelfDefine = 3
Algorithm = Entropy

chance = 0.0
carno = 0
BSid = 0
entry_in = []
bandwidth = []
BSs = []
Cars = []
PrTable = []
handoffTimes = 0


class Car:
    def __init__(self, x, y, dir, no):
        self.x = x
        self.y = y
        self.dir = dir
        self.no = no
        self.BSid = 0
        self.Pr = 0.0
        self.t_call = 0
        self.t_release = 0
        self.isCalling = False
        self.carUI = cityUI.draw_single_car(
            w, self.x, self.y)
        self.counter = 0

    def move(self):
        # update car's position by 1 time quantum
        if self.x % mapEdge == 0 and self.y % mapEdge == 0:
            # change direction
            r = random.randint(1, 32)
            if r <= 16:  # forward
                self.dir = transition[self.dir][0]
            elif r <= 18:  # turn around
                self.dir = transition[self.dir][1]
            elif r <= 25:  # turn left
                self.dir = transition[self.dir][2]
            elif r <= 32:  # turn right
                self.dir = transition[self.dir][3]

        # then drive directly (modify x, y)
        if self.dir == UP:
            self.y = round(self.y - carSpeed, 0)
        elif self.dir == DOWN:
            self.y = round(self.y + carSpeed, 0)
        elif self.dir == LEFT:
            self.x = round(self.x - carSpeed, 0)
        elif self.dir == RIGHT:
            self.x = round(self.x + carSpeed, 0)

        # out of bound, so set to -1
        # move car UI here
        if self.x < 0.0 or self.x > mapEdge * 10 or self.y < 0.0 or self.y > mapEdge * 10:
            # means the car is about to be remove
            w.delete(self.carUI)
            self.x = -1
            self.y = -1
        else:
            if self.x % 100 == 0 and self.y % 100 == 0:
                if self.dir == UP:
                    w.move(self.carUI, 0, -2)
                elif self.dir == DOWN:
                    w.move(self.carUI, 0, 2)
                elif self.dir == LEFT:
                    w.move(self.carUI, -2, 0)
                elif self.dir == RIGHT:
                    w.move(self.carUI, 2, 0)

        # update counter
        self.counter = self.counter % (mapEdge * 4) + 1

        # change the color of cars
        if self.isCalling == True:
            w.itemconfig(self.carUI, fill='yellow')
        else:
            w.itemconfig(self.carUI, fill='blue')

    def updatePr(self):
        # update Pr corresponded to the BS you connected
        for tp in PrTable[int(self.y / carSpeed)][int(self.x / carSpeed)]:
            if tp[1] == self.BSid:
                self.Pr = tp[0]
                break

    def checkHandoff(self, alg):
        isHandoff = False

        if alg == Minimum:
            if self.Pr < Pmin:
                for tp in PrTable[int(self.y / carSpeed)][int(self.x / carSpeed)]:
                    if tp[0] > self.Pr:
                        isHandoff = True
                        self.Pr = tp[0]
                        self.BSid = tp[1]
        elif alg == BestEffort:
            for tp in PrTable[int(self.y / carSpeed)][int(self.x / carSpeed)]:
                if tp[0] > self.Pr:
                    isHandoff = True
                    self.Pr = tp[0]
                    self.BSid = tp[1]
        elif alg == Entropy:
            for tp in PrTable[int(self.y / carSpeed)][int(self.x / carSpeed)]:
                if (tp[0] - self.Pr) > entropy:
                    isHandoff = True
                    self.Pr = tp[0]
                    self.BSid = tp[1]
        elif alg == SelfDefine:
            for tp in PrTable[int(self.y / carSpeed)][int(self.x / carSpeed)]:
                if self.counter == 0:
                    if tp[0] > self.Pr:
                        isHandoff = True
                        self.Pr = tp[0]
                        self.BSid = tp[1]
                else:
                    if (tp[0] - self.Pr) > entropy:
                        isHandoff = True
                        self.Pr = tp[0]
                        self.BSid = tp[1]

        return isHandoff

    def startRelease(self):
        self.t_release = int(round(numpy.random.normal(releaseTime, 5), 0))
        self.isCalling = False

    def startNewCall(self):
        self.t_call = int(round(numpy.random.normal(callTime, 5), 0))
        self.isCalling = True


class BS:
    def __init__(self, x, y, band, id):
        self.x = x
        self.y = y
        self.band = band
        self.id = id


def cleanOutbounder():
    for c in list(Cars):
        if c.x == -1 and c.y == -1:
            # print("Car ", c.no, c.x, c.y, "Cancel!")
            Cars.remove(c)


def poissonProb(n, t, lam):  # t (sec)
    # (n, t) should be (1, 1)
    mean = lam * t
    prob = math.exp(-1 * mean) * mean ** n / math.factorial(n)
    return (round(prob, 3))


def canCreate(q, p):
    draw = random.randint(1, p)
    if draw <= q:
        return True
    else:
        return False


def offsetsBS(x, y):
    r = random.randint(1, 4)
    cx = x
    cy = y
    if r == 1:
        cy = cy - offsetVal
    elif r == 2:
        cy = cy + offsetVal
    elif r == 3:
        cx = cx - offsetVal
    elif r == 4:
        cx = cx + offsetVal

    return (cx, cy)


def carIn(numer, denom):   # decides what entry car may come in
    # numer = chance * 1000
    # denom = 1000
    global carno
    for i in range(36):
        if canCreate(numer, denom) == True:
            x = entry_in[i][0]
            y = entry_in[i][1]
            d = entry_in[i][2]
            # print("Car created!", "X:", x, "Y: ", y)
            new_car = Car(x, y, d, carno)
            carno = carno + 1
            Cars.append(new_car)


def calculatePr(band, Cx, Cy, Bx, By):
    d = math.sqrt((Cx - Bx) ** 2 + (Cy - By) ** 2)
    d = (d / 1000)  # km
    Lp = 32.45 + 20 * math.log10(band) + 20 * math.log10(d)
    Pr = round(Pt - Lp, 2)

    return Pr


# init car come-in chance
chance = poissonProb(1, 1, Lambda)
# With the aim of lowering the burden of computing
chance = round(chance / 10, 3)

# init a list contains all position cars may come
for i in range(9):
    entry_in.append((float(i + 1) * mapEdge, 0.0, DOWN))  # At top
for i in range(9):
    entry_in.append((float(i + 1) * mapEdge, mapEdge * 10, UP))  # At bottom
for i in range(9):
    entry_in.append((mapEdge * 10, float(i + 1) * mapEdge, LEFT))  # At right
for i in range(9):
    entry_in.append((0.0, float(i + 1) * mapEdge, RIGHT))  # At left

# init all bs bandwidth list
for i in range(10):
    bandwidth.append(100 + i * 100)

# build BS
for i in range(10):
    for j in range(10):
        if canCreate(1, 10) == True:
            coord = offsetsBS(mapEdge / 2 + j * mapEdge,
                              mapEdge / 2 + i * mapEdge)
            new_band = bandwidth[random.randint(0, 9)]
            bs = BS(coord[0], coord[1], new_band, BSid)
            BSid = BSid + 1
            BSs.append(bs)

print('environment is built ')

# fill up Pr lookup table
for i in range(0, int((mapEdge / carSpeed) * 10) + 1):
    row = []
    for j in range(0, int((mapEdge / carSpeed) * 10) + 1):
        PrOnSpotList = []
        if i % int(mapEdge/carSpeed) != 0 and j % int(mapEdge/carSpeed) != 0:
            row.append(PrOnSpotList)
            continue
        for b in BSs:
            eachBSPr = calculatePr(b.band, float(
                j) * carSpeed, float(i) * carSpeed, b.x, b.y)
            PrOnSpotList.append((eachBSPr, b.id))
        row.append(PrOnSpotList)
    PrTable.append(row)

print('Pr lookup table is set')

############################# Drawing UI ################################

# set UI canvas
canvas_width = 700
canvas_height = 700
master = Tk()
master.title('network simulation')
w = Canvas(master, width=canvas_width, height=canvas_height)
time_label = w.create_text(50, 580, text="current time: ",
                           fill="black", font='Arial 14 bold', anchor='nw')
carNum_label = w.create_text(50, 610, text="current car number: ",
                             fill="black", font='Arial 14 bold', anchor='nw')
calling_label = w.create_text(50, 640, text="current on call car: ",
                              fill="black", font='Arial 14 bold', anchor='nw')
handoff_label = w.create_text(50, 670, text="handoff times: ",
                              fill="black", font='Arial 14 bold', anchor='nw')

# draw roads
cityUI.draw_roads(w)

cityUI.draw_bs(w, BSs)

# start simulation!
for t in range(10000):
    calling = 0
    carIn(int(chance * 1000), 1000)
    for c in Cars:
        c.move()
        if c.x >= 0 and c.y >= 0:   # the car hasn't been tagged
            c.updatePr()
        # call or release
        if c.t_call <= 0 and c.isCalling == True:
            c.startRelease()

        if c.t_release <= 0 and c.isCalling == False:
            c.startNewCall()

        # count down
        if c.t_call > 0:
            c.t_call = c.t_call - 1
        if c.t_release > 0:
            c.t_release = c.t_release - 1

        # if handoff is needed
        # the car hasn't been tagged and is calling
        # count how many cars are calling now
        if c.x >= 0 and c.y >= 0 and c.isCalling == True:
            calling += 1
            if c.checkHandoff(Algorithm) == True:
                handoffTimes = handoffTimes + 1

    w.itemconfig(carNum_label, text='current car number: ' + str(len(Cars)))
    w.itemconfig(handoff_label, text='handoff times: ' + str(handoffTimes))
    w.itemconfig(time_label, text='actual time: ' + str(t) + ' s')
    w.itemconfig(calling_label, text='current on call car: ' + str(calling))
    w.update_idletasks()
    cleanOutbounder()
