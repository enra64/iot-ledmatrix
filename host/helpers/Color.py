import colorsys
from typing import Tuple

class Color():
    def __init__(self, r: int = 0, g: int = 0, b: int = 0):
        """
        
        :param r: 0-255 value 
        :param g: 0-255 value
        :param b: 0-255 value
        """
        self.r = r / 255
        self.g = g / 255
        self.b = b / 255

    @staticmethod
    def from_rgb(rgb: Tuple[int]):
        return Color(rgb[0], rgb[1], rgb[2])

    def get_rgb(self):
        """
        Get an rgb tuple describing this color
        :return: 0-255 value, (r,g,b) tuple 
        """
        return int(round(self.r * 255)), int(round(self.g * 255)), int(round(self.b * 255))

    def set_rgb(self, rgb):
        """
        Set an rgb tuple that will replace this color
        :param rgb: 0-255 values (r,g,b)
        :return: nothing
        """
        self.r = rgb[0] / 255
        self.g = rgb[1] / 255
        self.b = rgb[2] / 255

    def __set_rgb_no_normalization(self, rgb):
        """
        Set an rgb tuple that will replace this color
        :param rgb: 0-1 values (r,g,b)
        :return: nothing
        """
        self.r = rgb[0]
        self.g = rgb[1]
        self.b = rgb[2]

    def get_hls(self):
        return colorsys.rgb_to_hls(self.r, self.g, self.b)

    def get_hsv(self):
        return colorsys.rgb_to_hsv(self.r, self.g, self.b)

    def set_luminance(self, luminance):
        hls = list(colorsys.rgb_to_hls(self.r, self.g, self.b))
        hls[1] = luminance
        self.__set_rgb_no_normalization(colorsys.hls_to_rgb(*hls))

    def set_hue(self, hue):
        hls = list(colorsys.rgb_to_hls(self.r, self.g, self.b))
        hls[0] = hue
        self.__set_rgb_no_normalization(colorsys.hls_to_rgb(*hls))

    def set_value(self, value):
        hsv = list(colorsys.rgb_to_hsv(self.r, self.g, self.b))
        hsv[2] = value
        self.__set_rgb_no_normalization(colorsys.hsv_to_rgb(*hsv))

    def set_saturation(self, saturation):
        hsv = list(colorsys.rgb_to_hsv(self.r, self.g, self.b))
        hsv[1] = saturation
        self.__set_rgb_no_normalization(colorsys.hsv_to_rgb(*hsv))

    def change_luminance(self, change_function):
        hls = list(colorsys.rgb_to_hls(self.r, self.g, self.b))
        hls[1] = change_function(hls[1])
        self.__set_rgb_no_normalization(colorsys.hls_to_rgb(*hls))

    def change_hue(self, change_function):
        hls = list(colorsys.rgb_to_hls(self.r, self.g, self.b))
        hls[0] = change_function(hls[0])
        self.__set_rgb_no_normalization(colorsys.hls_to_rgb(*hls))

    def change_value(self, change_function):
        hsv = list(colorsys.rgb_to_hsv(self.r, self.g, self.b))
        hsv[2] = change_function(hsv[2])
        self.__set_rgb_no_normalization(colorsys.hsv_to_rgb(*hsv))

    def change_saturation(self, change_function):
        hls = list(colorsys.rgb_to_hls(self.r, self.g, self.b))
        hls[2] = change_function(hls[2])
        self.__set_rgb_no_normalization(colorsys.hls_to_rgb(*hls))