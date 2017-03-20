import time
import random

from matgraphics import Canvas


class echo_test:
    def __init__(self, canvas):
        print("print_tester: init called")
        self.next_draw = (0, 0)

    def update(self, canvas):
        print("print_tester: received update call at " + str(time.time()), end="")
        self.next_draw = (random.randint(0, canvas.width - 1), random.randint(0, canvas.height - 1))
        print("chose " + str(self.next_draw[0]) + "," + str(self.next_draw[1]))

    def draw(self, canvas: Canvas):
        print("print_tester: received draw call")
        canvas.draw_pixel(self.next_draw[0], self.next_draw[1], 255, 255, 255)
        print(repr(canvas))

    def on_data(self, json, source_id):
        pass

    def exit(self):
        print("print_tester: exiting")