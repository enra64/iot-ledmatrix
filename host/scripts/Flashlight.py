from colour import Color

from CustomScript import CustomScript
from Canvas import Canvas


class Flashlight(CustomScript):
    def __init__(self, canvas, send_object, send_object_to_all, start_script, restart_self, set_frame_period,
                 set_frame_rate, get_connected_clients):
        super().__init__(canvas, send_object, send_object_to_all, start_script, restart_self, set_frame_period,
                         set_frame_rate, get_connected_clients)
        self.enable = True

    def draw(self, canvas: Canvas):
        if self.enable:
            canvas.clear(Color("white"))
        else:
            canvas.clear()

    def on_data(self, json, source_id):
        if 'enable' in json:
            self.enable = json['enable']
