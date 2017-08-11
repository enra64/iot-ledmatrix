import datetime
import json
from typing import List
import logging

from helpers.Color import Color

from CustomScript import CustomScript
from Canvas import Canvas, Rect


def round_to_five(integer: int):
    return int(5 * round(float(integer) / 5))


class Wordclock(CustomScript):
    def __init__(self, canvas, send_object, send_object_to_all, start_script, restart_self, set_frame_period,
                 set_frame_rate, get_connected_clients):
        super().__init__(canvas, send_object, send_object_to_all, start_script, restart_self, set_frame_period,
                         set_frame_rate, get_connected_clients)
        # request updates to happen in 5-second-intervals
        set_frame_period(10)

        self.__create_word_rectangles()

        self.logger = logging.getLogger("script:wordclock")

    def __create_word_rectangles(self):
        config_json = json.load(open("assets/merets_wordclock_config.json", "r"))
        print(config_json)

    def __get_rectangles(self, now_time) -> List[Rect]:
        out_rectangles = []

        rounded_minutes = round_to_five(now_time.minute)

        if now_time.minute < 35:
            out_rectangles.append(self.minutes[rounded_minutes])
            if not (rounded_minutes == 15 or rounded_minutes == 30):
                out_rectangles.append(self.others["minutes"])
            out_rectangles.append(self.others["past"])
            out_rectangles.append(self.hour_rects[now_time.hour % 12])
        else:
            out_rectangles.append(self.minutes[60 - rounded_minutes])
            if rounded_minutes != 15:
                out_rectangles.append(self.others["minutes"])
            out_rectangles.append(self.others["to"])
            out_rectangles.append(self.hour_rects[(now_time.hour + 1) % 12])

        return out_rectangles

    def draw(self, canvas: Canvas):
        word_rectangles = self.__get_rectangles(datetime.datetime.now())
        print(len(word_rectangles))
        canvas.clear()
        for rectangle in word_rectangles:
            canvas.draw_rectangle(rectangle, Color(0, 255, 0))

    def on_data(self, json, source_id):
        pass