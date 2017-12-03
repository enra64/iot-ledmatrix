import datetime
import json
from json import JSONDecodeError
from typing import List, Dict
import logging

import math

from helpers.Color import Color

from CustomScript import CustomScript
from Canvas import Canvas, Rect


class Word:
    def __init__(self, id, dict):
        self.id = id
        self.display_string = dict["word"]
        self.rectangle = self.__parse_rect(dict["rect"])
        self.category = dict["category"]
        self.info = dict["info"]
        self.color = Color(255, 0, 0)

    @staticmethod
    def __parse_rect(rectangle_list: Dict):
        return Rect(
            rectangle_list.get("x", 0),
            rectangle_list["y"],
            rectangle_list["width"],
            rectangle_list.get("height", 1)
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
        # config_file_path = "assets/config_ledmatrix_arnes_wordclock_lines_filled_with_other_letters.json"
        config_file_path = "assets/susannes_wordclock_config.json"
        self.logger.info("using {} as config".format(config_file_path))
        # config_file_path = "assets/merets_wordclock_config.json"

        self.logger.info("loading " + config_file_path)
        with open(config_file_path, 'r') as config_file:
            self.config_json = config_file.read()

        success = True
        try:
            self.__load_word_config()
        except JSONDecodeError as e:
            success = False
            self.logger.error(
                "could not load config file {} due to a decoding error: {}".format(config_file_path, e.msg))

        self.color_config = None
        try:
            self.__load_color_config()
        except JSONDecodeError as e:
            success = False
            self.logger.error(
                "could not load config file {} due to a decoding error: {}".format("wordclock_color_config.json", e.msg))

        if success:
            self.__send_config()

    def __load_word_config(self):
        self.config = json.loads(self.config_json)
        self.display_25_as_to_half = self.config["display_25_as_to_half"]
        self.has_specific_minutes_word = self.config["has_specific_minutes_word"]
        self.is_half_past_not_half_to = self.config["is_half_past_not_half_to"]
        self.words = []

        for i in range(len(self.config["config"])):
            self.words.append(Word(i, self.config["config"][i]))

    def __get_words(self, category: str, info) -> List[Rect]:
        category_words = [word for word in self.words if word.category.lower() == category.lower()]
        result = []
        for word in category_words:
            if (str(word.info)).lower() == str(info).lower():
                result.append(word)

        if len(result) == 0:
            self.logger.warning("unknown word requested with category " + category + " and info " + str(info))

        return result

    def __get_minute_bar(self) -> List[Rect]:
        return self.__get_words("minute_small_bar", "")

    def __get_applicable_words(self, now_time, explain: bool = False) -> List[Word]:
        """
        parse a time into rectangles
        :param now_time: the time to parse
        :param explain: if True, try to explain the choices made
        :return:
        """
        # bunch of helper functions to sort the words
        get_other = lambda other: self.__get_words("other", other)
        has_other = lambda other: len(get_other(other)) > 0
        get_minute = lambda minute: self.__get_words("minute_big", minute)
        get_hour = lambda hour: self.__get_words("hour", hour)
        
        result = []
        rounded_minutes = int(5 * round(float(now_time.minute) / 5))
        
        if explain:
            self.logger.info("rounded minutes are {}".format(rounded_minutes))

        # if we have an *it is*-word, always append it
        if has_other("itis"):
            result.extend(get_other("itis"))

        # special case: punkt
        if rounded_minutes == 0 or rounded_minutes == 60:
            if has_other("oclock"):
                result.extend(get_other("oclock"))
            result.extend(get_hour((now_time.hour + (rounded_minutes // 60)) % 12))
        # special case: fünf vor halb
        elif rounded_minutes == 25:
            if explain:
                self.logger.info("its 25 past something")
            if self.display_25_as_to_half:
                result.extend(get_other("to"))
                result.extend(get_minute(30))
            else:
                result.extend(get_other("past"))
                if self.has_specific_minutes_word:
                    result.extend(get_other("minutes"))
                result.extend(get_minute(20))

            if explain:
                self.logger.info("append '5 minutes' and the hour")
            result.extend(get_minute(5))
            result.extend(get_hour(now_time.hour % 12))
        # special case: fünf nach halb
        elif rounded_minutes == 35:
            if self.display_25_as_to_half:
                result.extend(get_other("past"))
                result.extend(get_minute(30))
            else:
                result.extend(get_other("to"))
                if self.has_specific_minutes_word:
                    result.extend(get_other("minutes"))
                result.extend(get_minute(20))

            result.extend(get_minute(5))
            result.extend(get_hour(now_time.hour % 12))
        elif rounded_minutes == 30:
            result.extend(get_minute(rounded_minutes))
            if self.is_half_past_not_half_to:
                result.extend(get_other("past"))
                result.extend(get_hour(now_time.hour % 12))
            else:
                result.extend(get_hour((now_time.hour + 1) % 12))
        elif rounded_minutes < 35:
            result.extend(get_minute(rounded_minutes))
            if not (rounded_minutes == 15 or rounded_minutes == 30) and self.has_specific_minutes_word:
                result.extend(get_other("minutes"))
            result.extend(get_other("past"))
            result.extend(get_hour(now_time.hour % 12))
        else:
            result.extend(get_minute(60 - rounded_minutes))
            # avoid printing
            if rounded_minutes != 15 and self.has_specific_minutes_word:
                result.extend(get_other("minutes"))
            result.extend(get_other("to"))
            result.extend(get_hour((now_time.hour + 1) % 12))

        return result

    def update(self, canvas):
        # request updates to happen in 5-second-intervals
        # self.set_frame_period(10)
        self.set_frame_rate(.3)
        self.debug_time_offset += 5

    def print_time(self, time):
        formatted_time = ":".join(str(time).split()[1].split(".")[0].split(":")[:2])
        self.logger.info("showing time {}".format(formatted_time))

    def __debug_print_rectangles(self, word_rectangles: List[Rect]):
        for rectangle in word_rectangles:
            self.logger.info(
                "rect at <{}, {}> size [{}, {}]".format(rectangle.x, rectangle.y, rectangle.width, rectangle.height))

    def draw(self, canvas: Canvas):
        offset_time = datetime.datetime.now() + datetime.timedelta(minutes=self.debug_time_offset)

        explain = False
        words = self.__get_applicable_words(offset_time, explain=explain)


        if explain:
            self.print_time(offset_time)
            self.__debug_print_rectangles([word.rectangle for word in words])

        canvas.clear()
        for word in words:
            if word is not None:
                canvas.draw_rectangle(word.rectangle, word.color)
        pass

    def __send_config(self):
        self.send_object_to_all(
            {
                "message_type": "wordclock_configuration",
                "config": self.config["config"],
                "lines": self.config["lines"]
            })
        if self.color_config is not None:
            self.send_object_to_all(
                {
                    "message_type": "wordclock_color_configuration",
                    "color_config": self.color_config
                })

    def on_client_connected(self, id):
        self.__send_config()

    def on_data(self, json, source_id):
        if "command" in json and json["command"] == "retry sending wordclock config":
            self.__send_config()
        elif "word_color_config" in json:
            self.__save_color_info(json["word_color_config"])
            self.__parse_color_info(json["word_color_config"])

        #print(json)

    def __to_rgb(self, android_color_int):
        r = (android_color_int & 0x00FF0000) >> 16
        g = (android_color_int & 0x0000FF00) >> 8
        b = (android_color_int & 0x000000FF) >> 0
        return Color(r, g, b)

    def __parse_color_info(self, color_array):
        for color_info in color_array:
            self.words[color_info["id"]].color = self.__to_rgb(color_info["clr"])

    def __save_color_info(self, color_array):
        with open("wordclock_color_config.json", "w") as out_file:
            json.dump(color_array, out_file)

    def __load_color_config(self):
        try:
            with open("wordclock_color_config.json", "r") as in_file:
                self.color_config = json.load(in_file)
                self.__parse_color_info(self.color_config)
        except FileNotFoundError:
            self.logger.info("no wordclock color config found. first start?")
        except JSONDecodeError:
            self.logger.error("bad wordclock color config found! re-send from app...")
