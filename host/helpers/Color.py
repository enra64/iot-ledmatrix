import colorsys
from typing import Tuple

import random

from helpers import utils


def float_is_close(a, b, relative_tolerance=1e-09, absolute_tolerance=0.0):
    """Check whether two floats are similar. needed for python 3.4"""
    return abs(a - b) <= max(relative_tolerance * max(abs(a), abs(b)), absolute_tolerance)


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

    Following special color generation methods are available:
        * :meth:`random_color`
        * :meth:`random_color_bounded`
        * :meth:`from_single_color`
        * :meth:`from_rgb`
        
    To quickly get information, you may use
        * :meth:`is_black`
        * :meth:`is_white`

    To create new color instances, you may use:
        * :meth:`__init__`, the constructor with r, g and b parameters
        * :meth:`from_rgb`, which will return a color instance from the rgb tuple
        * :meth:`from_aarrggbb_int`, which can parse ARGB color integers (as they are, incidentally, used in android)
        * :meth:`get_copy`, which will return a copy of this color

    To get a copied instance with modified properties, the following methods are available:
        * :meth:`get_copy_with_value`, which changes the value of the returned copy

    Alternative representations may be accessed via:
        * :meth:`get_hls`: get as 0-1 floats in HLS color space
        * :meth:`get_hsv`, get as 0-1 floats in HSV color space
        * :meth:`get_aarrggbb_int`, as 32-bit fully opaque ARGB integer


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

        assert isinstance(r, int), "red passed to the Color constructor must be an integer!"
        assert isinstance(g, int), "green passed to the Color constructor must be an integer!"
        assert isinstance(b, int), "blue passed to the Color constructor must be an integer!"

        self.__r = r / 255  # type: float
        self.__g = g / 255  # type: float
        self.__b = b / 255  # type: float

    @staticmethod
    def from_aarrggbb_int(android_color_int: int):
        """
        Convert an android color int to this color class.

        :param android_color_int:
        :return:
        """
        r = (android_color_int & 0x00FF0000) >> 16
        g = (android_color_int & 0x0000FF00) >> 8
        b = (android_color_int & 0x000000FF) >> 0
        return Color(r, g, b)

    @staticmethod
    def from_rgb(rgb: Tuple[int, int, int]):
        """
        Create a new color instance
        :param rgb: tuple of 0-255 rgb color component values
        :return: color instance representing the tuple
        """
        return Color(rgb[0], rgb[1], rgb[2])

    @staticmethod
    def random_color():
        """
        Return a new completely random color

        :return: new random color
        """
        return Color(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

    @staticmethod
    def random_color_bounded(red_bounds: Tuple[int, int] = (0, 255),
                             green_bounds: Tuple[int, int] = (0, 255),
                             blue_bounds: Tuple[int, int] = (0, 255)):
        """
        Return a new random color with boundaries for the possible color extremes

        :param red_bounds: A tuple of (min_val_incl, max_val_incl) for red
        :param green_bounds: A tuple of (min_val_incl, max_val_incl) for green
        :param blue_bounds: A tuple of (min_val_incl, max_val_incl) for blue
        :return: new random color within boundaries
        """
        return Color(random.randint(*red_bounds), random.randint(*green_bounds), random.randint(*blue_bounds))

    @staticmethod
    def from_single_color(all_component_value: int):
        """
        Create a new color where each RGB component has the same value

        :param all_component_value: the value for each component
        :return: new color, where rgb = (val, val, val)
        """
        return Color(all_component_value, all_component_value, all_component_value)

    def get_aarrggbb_int(self) -> int:
        """
        Return this color as AARRGGBB, where AA is always 255 (fully opaque).

        :return: color int that can be used to specify a color in android
        """
        r, g, b = self.get_rgb()
        return 0xFF000000 | (r << 16) | (g << 8) | (b << 0)

    def get_rgb(self):
        """
        Get an rgb tuple describing this color
        :return: 0-255 value, (r,g,b) tuple 
        """
        # fuck rounding, humans cant see shit anyways, and this function gets called _really_ often
        return int(self.__r * 255), int(self.__g * 255), int(self.__b * 255)

    def get_copy(self):
        """
        Get a new copy of this exact color.
        :return: a new copy of this exact color
        """
        return Color.from_rgb(self.get_rgb())

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

    def set_rgb(self, rgb):
        """
        Set an rgb tuple that will replace this color
        
        :param rgb: 0-255 values (r,g,b)
        :return: nothing
        """
        self.__r = rgb[0] / 255
        self.__g = rgb[1] / 255
        self.__b = rgb[2] / 255

    def change_rgb(self, changer):
        """
        Change the RGB values.
        
        :param changer: function(r, g, b) returning the new (r, g, b). In- and output are 0-1!
        :return: nothing
        """
        r, g, b = changer(self.__r, self.__g, self.__b)
        self.__r = utils.clamp(r, 0, 1)
        self.__g = utils.clamp(g, 0, 1)
        self.__b = utils.clamp(b, 0, 1)

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

    def get_value(self):
        """
        Convert this color to HSV and return the hsv value
        :return: normalized color value
        """
        return self.get_hsv()[2]

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

    def get_copy_with_value(self, value):
        """
        Return a copy of this color. The copy has its value set to the given parameter
        :param value: 0-1 normalized color value per hsv color model
        :return: copy of this color with modified value
        """
        copy = self.get_copy()
        copy.set_value(value)
        return copy

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

    # noinspection PyChainedComparisons
    def is_black(self, epsilon: float = 1e-09):
        """
        Test wether all components are almost at their minimum value. 
        :param epsilon: error margin allowed. comparisons are done on 0-1 colors!
        :return: True if black.
        """
        return self.__r < epsilon and self.__g < epsilon and self.__b < epsilon

    # noinspection PyChainedComparisons
    def is_white(self, epsilon: float = 1e-09):
        """
        Test wether all components are almost at their maximum value. 
        :param epsilon: error margin allowed. comparisons are done on 0-1 colors!
        :return: True if white.
        """
        return self.__r > 1 - epsilon and self.__g > 1 - epsilon and self.__b > 1 - epsilon
