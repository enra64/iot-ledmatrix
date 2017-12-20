import json
import logging
from json import JSONDecodeError
from typing import List, Dict

from helpers.Color import Color
from scripts._Wordclock.WordLogic import Word


def update_color_info(color_array: Dict, words: List[Word]):
    for color_info in color_array:
        words[color_info["id"]].rectangle.color = Color.from_aarrggbb_int(color_info["clr"])


def set_color(color: Color, words: List[Word]):
    for word in words:
        word.rectangle.color = color


def randomize_colors(words: List[Word], config_file_path: str):
    for word in words:
        word.color = Color.random_color_bounded((50, 255), (50, 255), (50, 255))

    save_color_info(config_file_path, get_color_config(words))


def read_color_config_file(config_file_path, words: List[Word]):
    logger = logging.getLogger("scripts:wordclock:colorlogic")

    try:
        with open(config_file_path, "r") as in_file:
            color_config = json.load(in_file)
            update_color_info(color_config, words)
    except FileNotFoundError:
        logger.info("no wordclock color config found at {}. first start?".format(config_file_path))
        set_color(Color.from_rgb((255, 255, 255)), words)
    except JSONDecodeError as e:
        logger.error("bad wordclock color config at {}! re-send from app...".format(config_file_path))
        set_color(Color.from_rgb((255, 255, 255)), words)


def save_color_info(config_path, color_array):
    with open(config_path, "w") as out_file:
        json.dump(color_array, out_file)


def get_color_config(words: List[Word]):
    """return color config of the word list as the json representation used for storage and exchange"""
    return [{"id": i, "clr": word.rectangle.color.get_aarrggbb_int()} for i, word in enumerate(words)]
