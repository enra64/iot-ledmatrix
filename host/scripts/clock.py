import datetime

import Canvas
from CustomScript import CustomScript
from helpers.Color import Color
from helpers.TextScroller import TextScroller


class clock(CustomScript):

    def __init__(self, canvas, send_object, send_object_to_all, start_script, restart_self, set_frame_period,
                 set_frame_rate, get_connected_clients):
        super().__init__(canvas, send_object, send_object_to_all, start_script, restart_self, set_frame_period,
                         set_frame_rate, get_connected_clients)

        self.set_frame_rate(15)

        self.display_minute = True
        self.color_delta = None
        self.color = Color()
        self.last_time, self.text, self.x, self.y = None, None, None, None

    def draw(self, canvas: Canvas):
        canvas.draw_text(self.text, self.x, self.y, self.color)

    def __set_text(self, text, canvas):
        self.text = canvas.render_text(text, size = 12)
        self.x = 0#(canvas.width - self.text.width) // 2
        self.y = 0#(canvas.height - self.text.height) // 2

    def __set_minute_or_hour(self, time, canvas):
        if self.display_minute:
            self.__set_text("%02i" % time.minute, canvas)
        else:
            self.__set_text("%02i" % time.hour, canvas)

    def update(self, canvas):
        time = datetime.datetime.now().time()

        if self.last_time is None or time.minute != self.last_time.minute:
            self.last_time = time
            self.__set_minute_or_hour(time, canvas)

        if self.color.is_black():
            self.display_minute = not self.display_minute
            self.__set_minute_or_hour(time, canvas)
            self.color_delta = 0.02
        elif self.color.is_white():
            self.color_delta = -0.02

        self.color.change_rgb(lambda r, g, b: (r + self.color_delta, g + self.color_delta, b + self.color_delta))
