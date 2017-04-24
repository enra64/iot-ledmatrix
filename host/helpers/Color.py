import colorsys
from typing import Tuple

import random


class Color():
    """
    The color class abstracts the color concept.
    Colors are most efficiently accessed with the rgb methods, as they are represented as such internally. All RGB values
    are expected to be in the range of 0-255, and HSV/HLS values must be in between zero and one.
    
    Functions to modify HSV/HLS values are provided, see:
        * :meth:`set_luminance`, where the luminance value can be set
        * :meth:`set_hue`, where the hue value can be set
        * :meth:`set_value`, where the value can be set
        * :meth:`set_saturation`, where the saturation value can set
        * :meth:`change_luminance`, where the luminance value can be changed with minimal computational effort
        * :meth:`change_hue`, where the hue value can be changed with minimal computational effort
        * :meth:`change_value`, where the value can be changed with minimal computational effort
        * :meth:`change_saturation`, where the saturation value can be changed with minimal computational effort
        
    To access rgb values, you may use
        * :meth:`get_rgb`
        * :meth:`get_red`
        * :meth:`get_green`
        * :meth:`get_blue`
        
    To create new color objects, you can use the constructor, which needs r, g, b parameters, or :meth:`from_rgb`, which
    will return a Color instance from the provided rgb tuple.
    """

    def __init__(self, r: int = 0, g: int = 0, b: int = 0):
        """
        Create a new color instance.
        
        :param r: 0-255 value for red component 
        :param g: 0-255 value for green component
        :param b: 0-255 value for blue component
        """
        assert 0 <= r <= 255, "red component must be >= 0 and <= 255"
        assert 0 <= g <= 255, "green component must be >= 0 and <= 255"
        assert 0 <= b <= 255, "blue component must be >= 0 and <= 255"

        self.__r = r / 255
        self.__g = g / 255
        self.__b = b / 255

    @staticmethod
    def from_rgb(rgb: Tuple[int]):
        """
        Create a new color instance
        :param rgb: tuple of 0-255 rgb color component values
        :return: color instance representing the tuple
        """
        return Color(rgb[0], rgb[1], rgb[2])

    def get_rgb(self):
        """
        Get an rgb tuple describing this color
        :return: 0-255 value, (r,g,b) tuple 
        """
        # fuck rounding, humans cant see shit anyways, and this function gets called _really_ often
        return int(self.__r * 255), int(self.__g * 255), int(self.__b * 255)

    def get_red(self):
        """
        Get red component.

        :return: 0-255 value 
        """
        return int(self.__r * 255)

    def get_green(self):
        """
        Get green component.

        :return: 0-255 value 
        """
        return int(self.__g * 255)

    def get_blue(self):
        """
        Get blue component.
        
        :return: 0-255 value 
        """
        return int(self.__b * 255)

    @staticmethod
    def random_color():
        """
        Return a new completely random color
        
        :return: new random color 
        """
        return Color(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

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
        """
        Convert this color to HLS and return it as a tuple
        
        :return: tuple of 0-1 HLS values
        """
        return colorsys.rgb_to_hls(self.__r, self.__g, self.__b)

    def get_hsv(self):
        """
        Convert this color to HSV and return it as a tuple
        
        :return: tuple of 0-1 HSV values
        """
        return colorsys.rgb_to_hsv(self.__r, self.__g, self.__b)

    def set_luminance(self, luminance):
        """
        Change the luminance value.
        
        :param luminance: float, 1-0
        :return: nothing
        """
        assert 0 <= luminance <= 1, " must be 1-normalised"
        hls = list(colorsys.rgb_to_hls(self.__r, self.__g, self.__b))
        self.__set_rgb_no_normalization(colorsys.hls_to_rgb(hls[0], luminance, hls[2]))

    def set_hue(self, hue):
        """
        Set the hue value for this color. The color will be converted to HLS and back.
        
        :param hue: new hue value, 0-1 
        :return: nothing
        """
        assert 0 <= hue <= 1, "hue must be 1-normalised"
        hls = colorsys.rgb_to_hls(self.__r, self.__g, self.__b)
        self.__set_rgb_no_normalization(colorsys.hls_to_rgb(hue, hls[1], hls[2]))

    def set_value(self, value):
        """
        Set the value for this color. The color will be converted to HSV and back.

        :param value: new value, 0-1 
        :return: nothing
        """
        assert 0 <= value <= 1, "value must be 1-normalised"
        hsv = colorsys.rgb_to_hsv(self.__r, self.__g, self.__b)
        self.__set_rgb_no_normalization(colorsys.hsv_to_rgb(hsv[0], hsv[1], value))

    def set_saturation(self, saturation):
        """
        Set the saturation for this color. The color will be converted to HSV and back.

        :param saturation: new saturation value, 0-1 
        :return: nothing
        """
        assert 0 <= saturation <= 1, "saturation must be 1-normalised"
        hsv = colorsys.rgb_to_hsv(self.__r, self.__g, self.__b)
        self.__set_rgb_no_normalization(colorsys.hsv_to_rgb(hsv[0], saturation, hsv[2]))

    def change_luminance(self, change_function):
        """
        Change the luminance value according to some function.
        
        :param change_function: will have the old luminance value as only parameter, and must return the new luminance value 
        :return: nothing
        """
        hls = colorsys.rgb_to_hls(self.__r, self.__g, self.__b)
        self.__set_rgb_no_normalization(colorsys.hls_to_rgb(hls[0], change_function(hls[1]), hls[2]))

    def change_hue(self, change_function):
        """
        Change the hue value according to some function.

        :param change_function: will have the old hue value as only parameter, and must return the new hue value 
        :return: nothing
        """
        hls = colorsys.rgb_to_hls(self.__r, self.__g, self.__b)
        self.__set_rgb_no_normalization(colorsys.hls_to_rgb(change_function(hls[0]), hls[1], hls[2]))

    def change_value(self, change_function):
        """
        Change the value according to some function.

        :param change_function: will have the old value as only parameter, and must return the new value 
        :return: nothing
        """
        hsv = colorsys.rgb_to_hsv(self.__r, self.__g, self.__b)
        self.__set_rgb_no_normalization(colorsys.hsv_to_rgb(hsv[0], hsv[1], change_function(hsv[2])))

    def change_saturation(self, change_function):
        """
        Change the saturation value according to some function.

        :param change_function: will have the old saturation value as only parameter, and must return the new saturation value 
        :return: nothing
        """
        hls = colorsys.rgb_to_hls(self.__r, self.__g, self.__b)
        self.__set_rgb_no_normalization(colorsys.hls_to_rgb(hls[0], hls[1], change_function(hls[2])))
