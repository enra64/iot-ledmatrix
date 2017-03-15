import time
import random

from matgraphics import Canvas


class gameoflife:
    def __init__(self, canvas):
        print("gameoflife: init called")


    def update(self, canvas):
        print("gameoflife: received update call at " + str(time.time()), end="")


    def draw(self, canvas: Canvas):
        print("gameoflife: received draw call")

        print(repr(canvas))

    def exit(self):
        print("gameoflife: exiting")