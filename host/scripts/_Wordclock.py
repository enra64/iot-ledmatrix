import datetime
import json
from json import JSONDecodeError
from typing import List, Dict
import logging

import math

from helpers.Color import Color

from CustomScript import CustomScript
from Canvas import Canvas, Rect


def clock_round_to_five(integer: int):
    if integer > 30:
        return int(5 * math.ceil(float(integer) / 5))
    else:
        return int(5 * math.floor(float(integer) / 5))


class Word:
    def __init__(self, id, dict):
        self.id = id
        self.display_string = dict["word"]
        self.position = dict["pos"]
        self.rectangle = self.__parse_rect(dict["rect"])
        self.category = dict["category"]
        self.info = dict["info"]

    @staticmethod
    def __parse_rect(rectangle_list: Dict):
        return Rect(
            rectangle_list["x"],
            rectangle_list["y"],
            rectangle_list["width"],
            rectangle_list["height"]
        )


class _Wordclock(CustomScript):
    def __init__(self, canvas, send_object, send_object_to_all, start_script, restart_self, set_frame_period,
                 set_frame_rate, get_connected_clients):
        super().__init__(canvas, send_object, send_object_to_all, start_script, restart_self, set_frame_period,
                         set_frame_rate, get_connected_clients)
        self.logger = logging.getLogger("script:wordclock")
        self.words = []
        self.debug_time_offset = 0

        # config_file_path = "assets/arnes_wordclock_config.json"
        config_file_path = "assets/config_ledmatrix_arnes_wordclock_lines_filled_with_other_letters.json"
        # config_file_path = "assets/merets_wordclock_config.json"
        self.logger.info("loading " + config_file_path)
        with open(config_file_path, 'r') as config_file:
            self.config_json = config_file.read()

        try:
            self.__load_word_config()
            self.__send_config()
        except JSONDecodeError as e:
            self.logger.error("could not load config file {} due to a decoding error: {}".format(config_file_path, e.msg))

    def __load_word_config(self):
        self.config = json.loads(self.config_json)
        self.display_25_as_to_half = self.config["display_25_as_to_half"]
        self.words = []

        for i in range(len(self.config["config"])):
            self.words.append(Word(i, self.config["config"][i]))

    def __get_word_rectangles(self, category: str, info) -> List[Rect]:
        category_words = [word for word in self.words if word.category.lower() == category.lower()]
        result = []
        for word in category_words:
            if (str(word.info)).lower() == str(info).lower():
                result.append(word.rectangle)

        if len(result) == 0:
            self.logger.warning("unknown word requested with category " + category + " and info " + str(info))

        return result

    def __get_minute(self, minute: int) -> List[Rect]:
        return self.__get_word_rectangles("minute_big", minute)

    def __get_hour(self, hour: int) -> List[Rect]:
        return self.__get_word_rectangles("hour", hour)

    def __get_other(self, other: str) -> List[Rect]:
        return self.__get_word_rectangles("other", other)

    def __get_minute_bar(self) -> List[Rect]:
        return self.__get_word_rectangles("minute_small_bar", "")

    def __get_small_minute(self, minute: int) -> List[Rect]:
        return self.__get_word_rectangles("minute_small_point", minute)

    def __get_rectangles(self, now_time) -> List[Rect]:
        out_rectangles = []

        rounded_minutes = clock_round_to_five(now_time.minute)

        if rounded_minutes == 25:
            # special case twenty-five past/fünf vor halb
            if self.display_25_as_to_half:
                out_rectangles.extend(self.__get_other("to"))
                out_rectangles.extend(self.__get_minute(30))
            else:
                out_rectangles.extend(self.__get_other("past"))
                out_rectangles.extend(self.__get_other("minutes"))
                out_rectangles.extend(self.__get_minute(20))

            out_rectangles.extend(self.__get_minute(5))
            out_rectangles.extend(self.__get_hour(now_time.hour % 12))
        elif rounded_minutes < 35:
            out_rectangles.extend(self.__get_minute(rounded_minutes))
            if not (rounded_minutes == 15 or rounded_minutes == 30):
                out_rectangles.extend(self.__get_other("minutes"))
            out_rectangles.extend(self.__get_other("past"))
            out_rectangles.extend(self.__get_hour(now_time.hour % 12))
        elif rounded_minutes == 35:
            # special case twenty-five
            if self.display_25_as_to_half:
                out_rectangles.extend(self.__get_other("past"))
                out_rectangles.extend(self.__get_minute(30))
            else:
                out_rectangles.extend(self.__get_other("to"))
                out_rectangles.extend(self.__get_other("minutes"))
                out_rectangles.extend(self.__get_minute(20))

            out_rectangles.extend(self.__get_minute(5))
            out_rectangles.extend(self.__get_hour(now_time.hour % 12))
        else:
            out_rectangles.extend(self.__get_minute(60 - rounded_minutes))
            if rounded_minutes != 15:
                out_rectangles.extend(self.__get_other("minutes"))
            out_rectangles.extend(self.__get_other("to"))
            out_rectangles.extend(self.__get_hour((now_time.hour + 1) % 12))

        return out_rectangles

    def update(self, canvas):
        # request updates to happen in 5-second-intervals
        # self.set_frame_period(10)
        self.set_frame_rate(2)
        self.debug_time_offset += 1

    def draw(self, canvas: Canvas):
        offset_time = datetime.datetime.now() + datetime.timedelta(minutes=self.debug_time_offset)
        word_rectangles = self.__get_rectangles(offset_time)
        print("drawing time:" + str(offset_time))
        canvas.clear()
        for rectangle in word_rectangles:
            if rectangle is not None:
                canvas.draw_rectangle(rectangle, Color(0, 255, 0))

    def __send_config(self):
        self.send_object_to_all(
            {
                "message_type": "wordclock_configuration",
                "config": self.config["config"],
                "lines": self.config["lines"]
            })

    def on_client_connected(self, id):
        self.__send_config()

    def on_data(self, json, source_id):
        print(json)
