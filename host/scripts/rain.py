from random import randint
from colour import Color

from CustomScript import CustomScript
from Canvas import Canvas

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
            for y in range(canvas.height-1, -1, -1):
                if(y > 0):
                    canvas.draw_pixel(x, y, canvas.get_color(x,y-1))
                    c = canvas.get_color(x,y-1)
                    c.luminance*=0.5
                    canvas.draw_pixel(x, y-1, c)

    def draw(self, canvas):
        self.frame+=1
        if(self.frame%3 == 0):
            frame = 0
            for i in range(0, 2):
                canvas.draw_pixel(randint(0,canvas.width-1), 0, Color(red = randint(0,255)/255, green = randint(0,255)/255, blue = randint(0,255)/255))


        #print(repr(canvas))
