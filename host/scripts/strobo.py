from helpers.Color import Color

from CustomScript import CustomScript
from Canvas import Canvas


class strobo(CustomScript):
    def __init__(self, canvas, send_object, send_object_to_all, start_script, restart_self, set_frame_period,
                 set_frame_rate, get_connected_clients):
        super().__init__(canvas, send_object, send_object_to_all, start_script, restart_self, set_frame_period,
                         set_frame_rate, get_connected_clients)
        self.set_frame_period(0.35)
        self.count = 0

    def update(self, canvas):
        if ((self.count % 3) == 0):
            canvas.clear(Color(255, 255, 255))
            self.count+=1
        else:
            canvas.clear()
            self.count+=1
