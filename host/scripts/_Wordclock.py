import datetime
import json
from typing import List
import logging

from helpers.Color import Color

from CustomScript import CustomScript
from Canvas import Canvas, Rect


def round_to_five(integer: int):
    return int(5 * round(float(integer) / 5))


class Word:
    def __init__(self, id, dict):
        self.id = id
        self.display_string = dict["word"]
        self.position = dict["pos"]
        self.rectangle = self.__parse_rect(dict["rect"])
        self.category = dict["category"]
        self.info = dict["info"]

    @staticmethod
    def __parse_rect(rectangle_list: List[int]):
        return Rect(
            rectangle_list[2],
            rectangle_list[3],
            rectangle_list[0],
            rectangle_list[1]
        )


class _Wordclock(CustomScript):
    def __init__(self, canvas, send_object, send_object_to_all, start_script, restart_self, set_frame_period,
                 set_frame_rate, get_connected_clients):
        super().__init__(canvas, send_object, send_object_to_all, start_script, restart_self, set_frame_period,
                         set_frame_rate, get_connected_clients)
        # request updates to happen in 5-second-intervals
        set_frame_period(10)
        self.logger = logging.getLogger("script:wordclock")
        self.words = []

        with open("assets/merets_wordclock_config.json", 'r') as config_file:
            self.config_json = config_file.read()

        self.__load_word_config()
        self.__send_config()

    def __load_word_config(self):
        self.config = json.loads(self.config_json)
        self.words = []

        for i in range(len(self.config)):
            self.words.append(Word(i, self.config[i]))

    def __get_word_rect(self, category: str, info) -> Rect:
        category_words = [word for word in self.words if word.category == category]
        for word in category_words:
            if str(word.info) == str(info):
                return word.rectangle
        self.logger.warning("unknown word requested with category " + category + " and  info " + str(info))
        return None

    def __get_minute(self, minute: int):
        return self.__get_word_rect("minute_big", minute)

    def __get_hour(self, hour: int):
        return self.__get_word_rect("hour", hour)

    def __get_other(self, other: str):
        return self.__get_word_rect("other", other)

    def __get_minute_bar(self):
        return self.__get_word_rect("minute_small_bar", "")

    def __get_small_minute(self, minute: int):
        return self.__get_word_rect("minute_small_point", minute)

    def __get_rectangles(self, now_time) -> List[Rect]:
        out_rectangles = []

        rounded_minutes = round_to_five(now_time.minute)

        if now_time.minute < 35:
            out_rectangles.append(self.__get_minute(rounded_minutes))
            if not (rounded_minutes == 15 or rounded_minutes == 30):
                out_rectangles.append(self.__get_other("minutes"))
            out_rectangles.append(self.__get_other("past"))
            out_rectangles.append(self.__get_hour(now_time.hour % 12))
        else:
            out_rectangles.append(self.__get_minute(60 - rounded_minutes))
            if rounded_minutes != 15:
                out_rectangles.append(self.__get_other("minutes"))
            out_rectangles.append(self.__get_other("to"))
            out_rectangles.append(self.__get_hour((now_time.hour + 1) % 12))

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
