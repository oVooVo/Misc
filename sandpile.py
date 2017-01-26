#!/usr/bin/python3

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from timeit import default_timer as timer
import random

class Sandpile:
    def __init__(self, w, h):
        self.data = np.array([[ 0 for x in range(w) ] for y in range(h)])
        self.w = w
        self.h = h
    
    def set(self, x, y, i):
        self.data[x, y] = i

    def getData(self):
        t = [   
                [ 
                    self.data[x,y] for x in range(1, self.w - 1) 
                ] for y in range(1, self.h - 1)
            ]
        return np.array(t)
    
    def topple(self):
        todo = []
        for x in range(1, self.w - 1):
            for y in range(1, self.h - 1):
                if self.data[x, y] > 4:
                    todo.append((x, y))
        for x, y in todo:
            self.data[x, y] -= 4
            for dx, dy in [ (-1, 0), (1, 0), (0, -1), (0, 1) ]:
                self.data[x+dx, y+dy] += 1
        return len(todo) > 0

sp = Sandpile(21, 21);
figure = plt.figure()
image = plt.imshow(sp.getData(), interpolation='nearest', animated = True, vmin=0, vmax=4)

def run(i):
    sp.data[1, 1] += 5
    sp.data[sp.w-2, 1] += 5
    sp.data[1, sp.h-2] += 5
    sp.data[sp.w-2, sp.h-2] += 5
    sp.topple()
    image.set_array(sp.getData())
    return image

ani = animation.FuncAnimation(figure, run, interval=60)
plt.show()
