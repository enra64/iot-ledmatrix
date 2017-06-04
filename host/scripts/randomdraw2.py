from noise import snoise2
from helpers.Color import Color

from CustomScript import CustomScript
from Canvas import Canvas


class randomdraw2(CustomScript):
    def __init__(self, canvas, send_object, send_object_to_all, start_script, restart_self, set_frame_period,
                 set_frame_rate, get_connected_clients):
        super().__init__(canvas, send_object, send_object_to_all, start_script, restart_self, set_frame_period,
                         set_frame_rate, get_connected_clients)
        self.set_frame_period(1)
        self.octaves = 1
        self.freq = 12.0 * self.octaves 
        self.xoff = 0

    def update(self, canvas):
        # count the number of neighbours
        canvas.clear()
        for x in range(0, canvas.width):
            for y in range(0, canvas.height):
                noise=int(snoise2( (x+self.xoff) / self.freq, y / self.freq, self.octaves) * 127.0 + 128.0)
                if(noise > 200):
                    canvas.draw_pixel(x, y, Color(1, 41, 95))
                elif(noise > 170):
                    canvas.draw_pixel(x, y, Color(67, 127, 151))
                elif(noise > 140):
                    canvas.draw_pixel(x, y, Color(132, 147, 36))
                elif(noise > 110):
                    canvas.draw_pixel(x, y, Color(255, 179, 15))
                elif(noise > 80):
                    canvas.draw_pixel(x, y, Color(253, 21, 27))
                elif(noise > 50):
                    canvas.draw_pixel(x, y, Color(181, 189, 104))
                elif(noise > 20):
                    canvas.draw_pixel(x, y, Color(245, 151, 78))
                elif(noise > 0):
                    canvas.draw_pixel(x, y, Color(241, 85, 65))

        self.xoff+=1  
            # print(repr(canvas))
