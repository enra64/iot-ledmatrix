import datetime
import json
import logging
import math
from enum import Enum
from json import JSONDecodeError
from typing import List, Dict

from Canvas import Canvas, Rect
from helpers.Color import Color


class WordType(Enum):
    other = 0
    minute_big = 1
    hour = 2
    minute_small_bar = 3


class Word:
    def __init__(self, id, dict):
        self.id = id
        self.display_string = dict["word"]
        self.rectangle = self.__parse_rect(dict["rect"])
        self.category = WordType[dict["category"].lower()]
        self.info = dict["info"]
        self.color = Color(255, 255, 255)

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

        self.__parse_words()

    def __parse_words(self):
        for i in range(len(self.config["config"])):
            self.words.append(Word(i, self.config["config"][i]))

    def get_config(self) -> Dict:
        return self.config

    def get_all_words(self) -> List[Word]:
        return self.words

    def __get_words(self, category: WordType, info) -> List[Word]:
        """
        Retrieve a list of words applicable for the given category
        :param category: type of the word we have requested
        :param info: additional info to identify the word in the category
        :return: list of words matching the data
        """
        category_words = [word for word in self.words if word.category == category]
        result = []
        for word in category_words:
            if (str(word.info)).lower() == str(info).lower():
                result.append(word)

        #if len(result) == 0:
        #    self.logger.warning("unknown word requested with category {} and info {}".format(category.name, info))

        return result



    def get_current_rectangles(self, now_time: datetime, canvas: Canvas) -> List[Rect]:
        rounded_minutes = int(5 * round(float(now_time.minute) / 5))

        result = [word.rectangle for word in self.__get_applicable_words(rounded_minutes, now_time.hour)]
        result.extend(self.__get_minute_bar_rectangles(canvas, now_time, rounded_minutes))
        return result

    def __get_other(self, info) -> List[Word]:
        return self.__get_words(WordType.other, info)

    def __has_other(self, info) -> bool:
        return len(self.__get_other(info)) > 0

    def __get_minute(self, minute: int) -> List[Word]:
        return self.__get_words(WordType.minute_big, minute)

    def __get_hour(self, hour: int) -> List[Word]:
        return self.__get_words(WordType.hour, hour)

    def __oclock(self, result, minutes, hours):
        if self.__has_other("oclock"):
            result.extend(self.__get_other("oclock"))
        elif self.__has_other("itis"):
            result.extend(self.__get_other("itis"))
        result.extend(self.__get_hour((hours + (minutes // 60)) % 12))

    def __twenty_five_past(self, result, minutes, hours):
        if self.display_25_as_to_half:
            result.extend(self.__get_other("to"))
            result.extend(self.__get_minute(30))
        else:
            result.extend(self.__get_other("past"))
            if self.has_specific_minutes_word:
                result.extend(self.__get_other("minutes"))
            result.extend(self.__get_minute(20))

        result.extend(self.__get_minute(5))
        result.extend(self.__get_hour(hours % 12))

    def __half(self, result, _, hours):
        result.extend(self.__get_minute(30))

        if self.is_half_past_not_half_to:
            result.extend(self.__get_other("past"))
            result.extend(self.__get_hour(hours % 12))
        else:
            result.extend(self.__get_hour((hours + 1) % 12))

    def __twenty_five_to(self, result, _, hours):
        if self.display_25_as_to_half:
            result.extend(self.__get_other("past"))
            result.extend(self.__get_minute(30))
        else:
            result.extend(self.__get_other("to"))
            if self.has_specific_minutes_word:
                result.extend(self.__get_other("minutes"))
            result.extend(self.__get_minute(20))

        result.extend(self.__get_minute(5))
        result.extend(self.__get_hour(hours % 12))

    def __before_half(self, result, minutes, hours):
        result.extend(self.__get_minute(minutes))
        if not (minutes == 15 or minutes == 30) and self.has_specific_minutes_word:
            result.extend(self.__get_other("minutes"))
        result.extend(self.__get_other("past"))
        result.extend(self.__get_hour(hours % 12))

    def __after_half(self, result, minutes, hours):
        result.extend(self.__get_minute(60 - minutes))
        # avoid printing
        if minutes != 15 and self.has_specific_minutes_word:
            result.extend(self.__get_other("minutes"))
        result.extend(self.__get_other("to"))
        result.extend(self.__get_hour((hours + 1) % 12))

    def __get_applicable_words(self, rounded_minutes: int, hours: int) -> List[Word]:
        """
        parse a time into rectangles
        :param now_time: the time to parse
        :param explain: if True, try to explain the choices made
        :return:
        """

        result = []

        # if we have an *it is*-word, always append it
        if self.__has_other("itis"):
            result.extend(self.__get_other("itis"))

        if rounded_minutes == 0 or rounded_minutes == 60:
            self.__oclock(result, rounded_minutes, hours)
        elif rounded_minutes == 25:
            self.__twenty_five_past(result, rounded_minutes, hours)
        elif rounded_minutes == 35:
            self.__twenty_five_to(result, rounded_minutes, hours)
        elif rounded_minutes == 30:
            self.__half(result, rounded_minutes, hours)
        elif rounded_minutes < 35:
            self.__before_half(result, rounded_minutes, hours)
        else:
            self.__after_half(result, rounded_minutes, hours)

        return result

    def __get_minute_bar_rectangles(self, canvas: Canvas, now_time: datetime, rounded_minutes) -> List[Rect]:
        """
        Get rectangles describing the minute bar.

        The idea for reading the minute bar is: The bar displays the percentage to the next five-minute-block.

        :param canvas:
        :param now_time:
        :param rounded_minutes:
        :return:
        """
        result = []

        # get the color for the minute bar
        minute_word = self.__get_words(WordType.minute_small_bar, 0)[0]
        rect = minute_word.rectangle
        color = minute_word.color

        # translate the seconds range into two parts: # of full leds and activation percentage of the last leds
        passed_seconds_in_this_timeblock = \
            (now_time.minute % 5) * 60 \
            + now_time.second \
            + (now_time.microsecond / 1000000)
        available_seconds_in_this_timeblock = 5 * 60
        led_activation = (passed_seconds_in_this_timeblock / available_seconds_in_this_timeblock) * rect.width

        fully_activated_leds = int(math.floor(led_activation))
        remaining_led_percentage = led_activation - fully_activated_leds

        # use for left aligned rectangle
        #result.append(Rect(rect.x, rect.y, fully_activated_leds, rect.height, color))
        #result.append(Rect(fully_activated_leds, rect.y, 1, rect.height, color.get_copy_with_value(remaining_led_percentage)))

        # use for centered rectangle
        # fully activated length is always an odd number
        fully_activated_length = fully_activated_leds - (1 - fully_activated_leds % 2)
        # begin in center of matrix row
        begin_full_activation_bar = (canvas.width - fully_activated_length) // 2
        result.append(Rect(begin_full_activation_bar, rect.y, fully_activated_length, 1, color))

        # calculate & apply percentage of the not-fully-activated leds
        # the percentage not covered by fully activated leds
        remaining_led_percentage = led_activation - fully_activated_length
        # do not increase value above the one the fully activated lesd use, as that looks strange
        not_fully_activated_color = color.get_copy_with_value((remaining_led_percentage / 2) * color.get_value())
        # finally, apply the calculated values
        result.append(Rect(begin_full_activation_bar - 1, rect.y, 1, rect.height, not_fully_activated_color))
        result.append(Rect(begin_full_activation_bar + fully_activated_length, rect.y, 1, rect.height, not_fully_activated_color))


        return result