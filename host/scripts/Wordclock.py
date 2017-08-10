import datetime
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
        self.others = {
            "to": Rect(0, 3, 2, 1),
            "past": Rect(2, 3, 4, 1),
            "minutes": Rect(2, 3, 4, 1)
        }

        self.minutes = {
            0: Rect(4, 8, 7, 1),  # basically o'clock
            5: Rect(1, 2, 4, 5),
            10: Rect(1, 2, 4, 5),
            15: Rect(1, 2, 4, 5),
            20: Rect(1, 2, 4, 5),
            30: Rect(1, 2, 3, 4)
        }

        self.hour_rects = {
            0: Rect(0, 5, 6, 1),
            1: Rect(0, 4, 3, 1),
            2: Rect(3, 4, 3, 1),
            3: Rect(6, 3, 5, 1),
            4: Rect(6, 4, 4, 1),
            5: Rect(0, 8, 4, 1),
            6: Rect(8, 7, 3, 1),
            7: Rect(3, 7, 5, 1),
            8: Rect(6, 5, 5, 1),
            9: Rect(6, 6, 6, 1),
            10: Rect(0, 7, 3, 1),
            11: Rect(0, 6, 6, 1)
        }

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