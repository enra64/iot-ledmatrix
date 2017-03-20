import time
import random
import numpy as np

from matgraphics import Canvas

class gameoflife:
    def __init__(self, canvas, send_object, send_object_to_all):
        self.gameboard = np.zeros((canvas.height, canvas.width), dtype = bool)
        self.colorboard = np.zeros((canvas.height, canvas.width, 3), dtype = int)
        self.gameboard[2, 5:7] = True
        self.gameboard[3, 4:6] = True
        self.gameboard[4, 5] = True

    def roll_it(self, x, y):
        # rolls the matrix X in a given direction
        # x=1, y=0 on the left;  x=-1, y=0 right;
        # x=0, y=1 top; x=0, y=-1 down; x=1, y=1 top left; ...
        return np.roll(np.roll(self.gameboard, y, axis=0), x, axis=1)

    def update(self, canvas):
        # count the number of neighbours
        # the universe is considered toroidal
        Y = self.roll_it(1, 0) + self.roll_it(0, 1) + self.roll_it(-1, 0) \
            + self.roll_it(0, -1) + self.roll_it(1, 1) + self.roll_it(-1, -1) \
            + self.roll_it(1, -1) + self.roll_it(-1, 1)
        # game of life rules
        self.gameboard = np.logical_or(np.logical_and(self.gameboard, Y ==2), Y==3)
        self.gameboard = self.gameboard.astype(bool)
        # yield self.gameboard
        for x in range(0, canvas.width):
            for y in range(0, canvas.height):
                if self.gameboard[x][y] is True:
                    self.colorboard[x][y] = (125,125,125)
                if self.gameboard[x][y] is False:
                    self.colorboard[x][y] = (0,0,0)

    def on_data(self, recv_json, source_id):
        pass

    def draw(self, canvas: Canvas):
        for x in range(0, canvas.width):
            for y in range(0, canvas.height):
                if self.gameboard[x][y] is True:
                    canvas.draw_pixel(x, y, self.colorboard[x][y][0], self.colorboard[x][y][1], self.colorboard[x][y][2])

        #print(repr(canvas))

    def exit(self):
        pass
