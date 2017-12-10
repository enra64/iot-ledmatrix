import json
import logging
from json import JSONDecodeError
from typing import List, Dict

from helpers.Color import Color
from scripts._Wordclock.WordLogic import Word


def decode_android_color_int(android_color_int):
    r = (android_color_int & 0x00FF0000) >> 16
    g = (android_color_int & 0x0000FF00) >> 8
    b = (android_color_int & 0x000000FF) >> 0
    return Color(r, g, b)


def update_color_info(color_array: Dict, words: List[Word]):
    for color_info in color_array:
        words[color_info["id"]].color = decode_android_color_int(color_info["clr"])
        words[color_info["id"]].rectangle.color = decode_android_color_int(color_info["clr"])


def read_color_config_file(config_file_path, words: List[Word]):
    logger = logging.getLogger("scripts:wordclock:colorlogic")

    try:
        with open(config_file_path, "r") as in_file:
            color_config = json.load(in_file)
            update_color_info(color_config, words)
    except FileNotFoundError as e:
        logger.info("no wordclock color config found at {}. first start?".format(config_file_path))
        raise e
    except JSONDecodeError as e:
        logger.error("bad wordclock color config at {}! re-send from app...".format(config_file_path))
        raise e


def save_color_info(config_path, color_array):
    with open(config_path, "w") as out_file:
        json.dump(color_array, out_file)


def get_color_config(words: List[Word]):
    return [{"id": i, "clr": word.color} for i, word in enumerate(words)]
