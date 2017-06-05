from helpers.Color import Color

from CustomScript import CustomScript
from Canvas import Canvas


class point(CustomScript):
    def __init__(self, canvas, send_object, send_object_to_all, start_script, restart_self, set_frame_period,
                 set_frame_rate, get_connected_clients):
        super().__init__(canvas, send_object, send_object_to_all, start_script, restart_self, set_frame_period,
                         set_frame_rate, get_connected_clients)
        self.set_frame_period(1)

    def draw(self, canvas):
        for x in range(0, 10):
            canvas.draw_pixel(x, x, Color(255, 255, 255))
        canvas.draw_pixel(4, 7, Color(255, 255, 255))
