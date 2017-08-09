from typing import List
import datetime

from helpers.Color import Color

from CustomScript import CustomScript
from Canvas import Canvas, Rect


class Wordclock:
    def __init__(self):
        self.others = {
            "to": Rect(0, 3, 2, 1),
            "past": Rect(2, 3, 4, 1)
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

        pass

    @staticmethod
    def __round_to_five(integer:int):
        return int(5 * round(float(integer) / 5))

    def get_rectangles(self, now_time) -> List[Rect]:
        rects = []

        rounded_time = self.__round_to_five(now_time.minute)

        if now_time.minute < 35:
            rects.append(self.others["past"])
            rects.append(self.minutes[rounded_time])

        else:
            rects.append(self.others["to"])
            rects.append(self.minutes[60 - rounded_time])
            rects.append(self.hour_rects[(now_time.hour + 1)% 12])

        return rects


class Flashlight(CustomScript):
    def __init__(self, canvas, send_object, send_object_to_all, start_script, restart_self, set_frame_period,
                 set_frame_rate, get_connected_clients):
        super().__init__(canvas, send_object, send_object_to_all, start_script, restart_self, set_frame_period,
                         set_frame_rate, get_connected_clients)
        self.enable = True

    def draw(self, canvas: Canvas):
        if self.enable:
            canvas.clear(Color(255, 255, 255))
        else:
            canvas.clear()

    def on_data(self, json, source_id):
        if 'enable' in json:
            self.enable = json['enable']
