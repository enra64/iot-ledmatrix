import numpy as np
from random import randint
from colour import Color

from CustomScript import CustomScript
from Canvas import Canvas

class randomdraw(CustomScript):
    def __init__(self, canvas, send_object, send_object_to_all, start_script, restart_self, set_frame_period,
                 set_frame_rate, get_connected_clients):
        super().__init__(canvas, send_object, send_object_to_all, start_script, restart_self, set_frame_period,
                         set_frame_rate, get_connected_clients)
        self.set_frame_period(1)

    def update(self, canvas):
        # count the number of neighbours
        canvas.clear()
        for y in range(0, 25):
                canvas.draw_pixel(randint(0,9), randint(0,9), Color(red = randint(0,255)/255, green = randint(0,255)/255, blue = randint(0,255)/255))


        #print(repr(canvas))
