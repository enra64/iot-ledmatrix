import json
import logging
from json import JSONDecodeError
from typing import List, Dict

from helpers.Color import Color
from scripts._Wordclock.WordLogic import Word


def decode_android_color_int(android_color_int: int) -> Color:
    r = (android_color_int & 0x00FF0000) >> 16
    g = (android_color_int & 0x0000FF00) >> 8
    b = (android_color_int & 0x000000FF) >> 0
    return Color(r, g, b)


def encode_as_android_color_int(color: Color) -> int:
    r, g, b = color.get_rgb()
    assert 0 <= r <= 255, "r = {} not in uint8_t bounds".format(r)
    assert 0 <= g <= 255, "g = {} not in uint8_t bounds".format(g)
    assert 0 <= b <= 255, "b = {} not in uint8_t bounds".format(b)

    return (r << 16) & (g << 8) & (b << 0)


def update_color_info(color_array: Dict, words: List[Word]):
    for color_info in color_array:
        words[color_info["id"]].color = decode_android_color_int(color_info["clr"])
        words[color_info["id"]].rectangle.color = decode_android_color_int(color_info["clr"])


def set_color(color: Color, words: List[Word]):
    for word in words:
        word.color = color
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
        raise e


def save_color_info(config_path, color_array):
    with open(config_path, "w") as out_file:
        json.dump(color_array, out_file)


def get_color_config(words: List[Word]):
    """return color config of the word list as the json representation used for storage and exchange"""
    return [{"id": i, "clr": encode_as_android_color_int(word.color)} for i, word in enumerate(words)]
