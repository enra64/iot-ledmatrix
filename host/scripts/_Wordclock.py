import datetime
import json
from typing import List
import logging

from helpers.Color import Color

from CustomScript import CustomScript
from Canvas import Canvas, Rect


def round_to_five(integer: int):
    return int(5 * round(float(integer) / 5))


class _Wordclock(CustomScript):
    def __init__(self, canvas, send_object, send_object_to_all, start_script, restart_self, set_frame_period,
                 set_frame_rate, get_connected_clients):
        super().__init__(canvas, send_object, send_object_to_all, start_script, restart_self, set_frame_period,
                         set_frame_rate, get_connected_clients)
        # request updates to happen in 5-second-intervals
        set_frame_period(10)
        self.logger = logging.getLogger("script:wordclock")

        with open("assets/merets_wordclock_config.json", 'r') as config_file:
            self.config_json = config_file.read()

        self.__load_word_config()
        self.__send_config()

    def __load_word_config(self):
        self.config = json.loads(self.config_json)
        self.hours = self.config["hours"]
        self.minutes = self.config["minutes"]
        self.other = self.config["other"]

        print(self.config_json)

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

    def __send_config(self):
        self.send_object_to_all(
            {"message_type": "wordclock_configuration", "configuration": self.config["configuration"]})

    def on_client_connected(self, id):
        self.__send_config()

    def on_data(self, json, source_id):
        print(json)
        pass
