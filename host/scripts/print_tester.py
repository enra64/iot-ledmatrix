import time
import random

from matgraphics import Canvas


class print_tester:
    def __init__(self):
        print("print_tester: init called")
        self.next_draw = (0, 0)

    def update(self, canvas):
        print("print_tester: received update call at " + str(time.time()), end="")
        self.next_draw = (random.randint(0, canvas.width - 1), random.randint(0, canvas.height - 1))
        print("chose " + str(self.next_draw[0]) + "," + str(self.next_draw[1]))

        canvas.draw

    def draw(self, canvas: Canvas):
        print("print_tester: received draw call")
        canvas.draw_pixel(self.next_draw[0], self.next_draw[1], 255, 255, 255)
        print(repr(canvas))

    def exit(self):
        print("print_tester: exiting")