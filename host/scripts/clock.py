import datetime

import Canvas
from CustomScript import CustomScript
from helpers.TextScroller import TextScroller


class clock(CustomScript):

    def __init__(self, canvas, send_object, send_object_to_all, start_script, restart_self, set_frame_period,
                 set_frame_rate, get_connected_clients):
        super().__init__(canvas, send_object, send_object_to_all, start_script, restart_self, set_frame_period,
                         set_frame_rate, get_connected_clients)

        self.text_scroller = TextScroller(canvas)
        self.text_scroller.set_size(12)
        self.set_frame_rate(13)

        self.last_time = None

    def draw(self, canvas: Canvas):
        self.text_scroller.draw(canvas, clear=True)

    def update(self, canvas):
        time = datetime.datetime.now().time()

        if self.last_time is None or time.minute != self.last_time.minute:
            self.text_scroller.set_text("%i:%i" % (time.hour, time.minute))
            self.last_time = time

        self.text_scroller.update()
