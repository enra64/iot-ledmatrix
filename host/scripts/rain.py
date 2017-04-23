from random import randint
from helpers.Color import Color

from CustomScript import CustomScript


class rain(CustomScript):
    def __init__(self, canvas, send_object, send_object_to_all, start_script, restart_self, set_frame_period,
                 set_frame_rate, get_connected_clients):
        super().__init__(canvas, send_object, send_object_to_all, start_script, restart_self, set_frame_period,
                         set_frame_rate, get_connected_clients)
        #self.set_frame_period(0.2)
        self.frame = 0

    def update(self, canvas):
        # count the number of neighbours
        for x in range(0, canvas.width):
            for y in range(canvas.height-1, 0, -1):
                c = canvas.get_color(x, y - 1)
                canvas.draw_pixel(x, y, c)
                c.change_luminance(lambda lum: lum*0.5)
                canvas.draw_pixel(x, y-1, c)

    def draw(self, canvas):
        self.frame+=1
        if self.frame == 3:
            self.frame = 0
            for i in range(0, 2):
                canvas.draw_pixel(randint(0,canvas.width-1), 0, Color(randint(0,255), randint(0,255), randint(0,255)))


        #print(repr(canvas))
