import colorsys
from typing import Tuple

class Color():
    def __init__(self, r: int = 0, g: int = 0, b: int = 0):
        """
        
        :param r: 0-255 value 
        :param g: 0-255 value
        :param b: 0-255 value
        """
        self.__r = r / 255
        self.__g = g / 255
        self.__b = b / 255

    @staticmethod
    def from_rgb(rgb: Tuple[int]):
        return Color(rgb[0], rgb[1], rgb[2])

    def get_rgb(self):
        """
        Get an rgb tuple describing this color
        :return: 0-255 value, (r,g,b) tuple 
        """
        # fuck rounding, humans cant see shit anyways, and this function gets called _really_ often
        return int(self.__r * 255), int(self.__g * 255), int(self.__b * 255)

    def get_red(self):
        return int(self.__r * 255)

    def get_green(self):
        return int(self.__g * 255)

    def get_blue(self):
        return int(self.__b * 255)

    def set_rgb(self, rgb):
        """
        Set an rgb tuple that will replace this color
        :param rgb: 0-255 values (r,g,b)
        :return: nothing
        """
        self.__r = rgb[0] / 255
        self.__g = rgb[1] / 255
        self.__b = rgb[2] / 255

    def __set_rgb_no_normalization(self, rgb):
        """
        Set an rgb tuple that will replace this color
        :param rgb: 0-1 values (r,g,b)
        :return: nothing
        """
        self.__r = rgb[0]
        self.__g = rgb[1]
        self.__b = rgb[2]

    def get_hls(self):
        return colorsys.rgb_to_hls(self.__r, self.__g, self.__b)

    def get_hsv(self):
        return colorsys.rgb_to_hsv(self.__r, self.__g, self.__b)

    def set_luminance(self, luminance):
        hls = list(colorsys.rgb_to_hls(self.__r, self.__g, self.__b))
        self.__set_rgb_no_normalization(colorsys.hls_to_rgb(hls[0], luminance, hls[2]))

    def set_hue(self, hue):
        hls = colorsys.rgb_to_hls(self.__r, self.__g, self.__b)
        self.__set_rgb_no_normalization(colorsys.hls_to_rgb(hue, hls[1], hls[2]))

    def set_value(self, value):
        hsv = colorsys.rgb_to_hsv(self.__r, self.__g, self.__b)
        self.__set_rgb_no_normalization(colorsys.hsv_to_rgb(hsv[0], hsv[1], value))

    def set_saturation(self, saturation):
        hsv = colorsys.rgb_to_hsv(self.__r, self.__g, self.__b)
        self.__set_rgb_no_normalization(colorsys.hsv_to_rgb(hsv[0], saturation, hsv[2]))

    def change_luminance(self, change_function):
        hls = colorsys.rgb_to_hls(self.__r, self.__g, self.__b)
        self.__set_rgb_no_normalization(colorsys.hls_to_rgb(hls[0], change_function(hls[1]), hls[2]))

    def change_hue(self, change_function):
        hls = colorsys.rgb_to_hls(self.__r, self.__g, self.__b)
        self.__set_rgb_no_normalization(colorsys.hls_to_rgb(change_function(hls[0]), hls[1], hls[2]))

    def change_value(self, change_function):
        hsv = colorsys.rgb_to_hsv(self.__r, self.__g, self.__b)
        self.__set_rgb_no_normalization(colorsys.hsv_to_rgb(hsv[0], hsv[1], change_function(hsv[2])))

    def change_saturation(self, change_function):
        hls = colorsys.rgb_to_hls(self.__r, self.__g, self.__b)
        self.__set_rgb_no_normalization(colorsys.hls_to_rgb(hls[0], hls[1], change_function(hls[2])))