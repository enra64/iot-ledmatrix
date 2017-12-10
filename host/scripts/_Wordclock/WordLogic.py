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


class WordLogic:
    def __init__(self, config_file_path):
        self.logger = logging.getLogger("script:wordclock:logic")

        try:
            with open(config_file_path, "r") as config_file:
                self.config = json.load(config_file)
        except JSONDecodeError as e:
            self.logger.error("Wordclock configuration file '{}' contains invalid JSON!".format(config_file_path))
            raise e
        except FileNotFoundError as e:
            self.logger.error("Wordclock configuration file '{}' not found!".format(config_file_path))
            raise e

        self.display_25_as_to_half = self.config["display_25_as_to_half"]
        self.has_specific_minutes_word = self.config["has_specific_minutes_word"]
        self.is_half_past_not_half_to = self.config["is_half_past_not_half_to"]
        self.words = []

        for i in range(len(self.config["config"])):
            self.words.append(Word(i, self.config["config"][i]))

    def __get_words(self, category: str, info) -> List[Word]:
        category_words = [word for word in self.words if word.category.lower() == category.lower()]
        result = []
        for word in category_words:
            if (str(word.info)).lower() == str(info).lower():
                result.append(word)

        if len(result) == 0:
            self.logger.warning("unknown word requested with category " + category + " and info " + str(info))

        return result

    def __get_minute_bar(self) -> Word:
        matching_words = self.__get_words("minute_small_bar", 0)
        assert len(matching_words) == 1
        return matching_words[0]

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