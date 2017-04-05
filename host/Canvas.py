import logging

from fonts import Font
from colour import Color


class Canvas:
    """
    A canvas makes it easy to display using the matrix by providing a translation layer between pixels on a cartesian
    coordinate system and color data readable by the arduino and the WS2812B RGB leds.
    
    The canvas uses colors from the colour library to represent the requested colors. See https://github.com/vaab/colour
    
    The user functions are:
    
    * draw_pixel(x, y, color)
    * draw_line(x_start, y_start, x_end, y_end, color)
    * draw_rect(x, y, width, height, color)
    * draw_text(x, y, text, color, ignore_height_warning=False)
    * set_font(path, size)
    * clear(color)
    """

    def __init__(self, width, height):
        """
        Initialise a new canvas object.

        :param width: width of the canvas in pixels
        :param height: height of the canvas in pixels
        """
        self.width = width
        self.height = height
        self.led_count = width * height
        self.buffer_length = self.led_count * 3

        # create buffer underlying canvas
        self.data_buffer = bytearray(self.buffer_length)

        # "init" font
        self.font = None

        # get a logger
        self.logger = logging.getLogger("canvas")

    def get_pixel_index(self, x, y):
        """
        Convert a cartesian coordinate for an led into the index that represents red for that led in the buffer.

        Currently, the chaining is assumed to be in a zig-zag, as follows:
        
        +----+----+----+----+----+----+----+----+----+----+----+
        |    |col0|col1|col2|col3|col4|col5|col6|col7|col8|col9|
        +====+====+====+====+====+====+====+====+====+====+====+
        |row0| 99 | 98 | 97 | 96 | 95 | 94 | 93 | 92 | 91 | 90 |
        +----+----+----+----+----+----+----+----+----+----+----+
        |row1| 80 | 81 | 82 | 83 | 84 | 85 | 86 | 87 | 88 | 89 |
        +----+----+----+----+----+----+----+----+----+----+----+
        |row2| 79 | 78 | 77 | 76 | 75 | 74 | 73 | 72 | 71 | 70 |
        +----+----+----+----+----+----+----+----+----+----+----+
        |row3| 60 | 61 | 62 | 63 | 64 | 65 | 66 | 67 | 68 | 69 |
        +----+----+----+----+----+----+----+----+----+----+----+
        |row4| 59 | 58 | 57 | 56 | 55 | 54 | 53 | 52 | 51 | 50 |
        +----+----+----+----+----+----+----+----+----+----+----+
        |row5| 40 | 41 | 42 | 43 | 44 | 45 | 46 | 47 | 48 | 49 |
        +----+----+----+----+----+----+----+----+----+----+----+
        |row6| 39 | 38 | 37 | 36 | 35 | 34 | 33 | 32 | 31 | 30 |
        +----+----+----+----+----+----+----+----+----+----+----+
        |row7| 20 | 21 | 22 | 23 | 24 | 25 | 26 | 27 | 28 | 29 |
        +----+----+----+----+----+----+----+----+----+----+----+
        |row8| 19 | 18 | 17 | 16 | 15 | 14 | 13 | 12 | 11 | 10 |
        +----+----+----+----+----+----+----+----+----+----+----+
        |row9| 0  | 1  | 2  | 3  | 4  | 5  | 6  | 7  | 8  | 9  |
        +----+----+----+----+----+----+----+----+----+----+----+

        :param x: x coordinate of the led in the matrix (counted left-to-right)
        :param y: y coordinate of the led in the matrix (counted top-to-bottom)
        :return: index of the red value of that led (g, b, are +1, +2 of that position respectively) in the buffer
        """
        # this variable will have the final index
        index = 0

        # distinguish between row direction
        if y % 2 == 1:
            # odd rows are left-to-right, x can just be added
            index += x

            # invert y coordinate to align to leds; multiply by width to know how many leds are in series before the one
            index += (self.height - 1 - y) * self.width
        # even rows
        else:
            index += (self.height - y) * self.width
            # right-to-left, so x position is inverted
            index -= (x + 1)

        return index

    def get_red_index(self, x, y):
        """
        Pretty much like get_pixel_index, but this function returns the position of the red value of the given led in the
        byte buffer.
        
        :param x: x coordinate of led in cartesian system
        :param y: y coordinate of led in cartesian system
        :return: position of "red" in the background buffer 
        """
        return self.get_pixel_index(x, y) * 3

    def __write_color_at(self, x, y, color: Color):
        """
        Write a color at a specified position in the matrix
        
        :param x: x position of pixel; counted from zero beginning on the left, must be smaller than the canvas width
        :param y: y position of pixel; y is zero for the top row of pixels, must be smaller than the canvas height
        :param color: the color to be written to the pixel
        :return: nothing
        """
        color_in_255 = self.__color_to_255_rgb(color)
        red_index = self.get_red_index(x, y)
        self.data_buffer[red_index:red_index + 3] = color_in_255

    @staticmethod
    def __get_repr_color(color: Color) -> str:
        """
        Returns r(ed), g(reen), b(lue), .(lack), w(hite), matching the largest color component that the given color has.
        
        :param color: the color of which we want to get the largest component
        :return: r, g, b, . or w
        """
        rgb = color.get_rgb()

        # white and black have their own representations
        if rgb == (0, 0, 0):
            return '.'
        if rgb == (1, 1, 1):
            return 'w'

        # return the color with the greatest part
        largest_color_index = rgb.index(max(rgb))
        if largest_color_index == 0:
            return 'r'
        elif largest_color_index == 1:
            return 'g'
        return 'b'

    def get_color(self, x, y) -> Color:
        """
        Get a Color instance describing the color of the led at x,y
        
        :param x: x position of pixel; counted from zero beginning on the left, must be smaller than the canvas width
        :param y: y position of pixel; y is zero for the top row of pixels, must be smaller than the canvas height 
        :return: a Color instance
        """
        red_index = self.get_red_index(x, y)
        clr = self.data_buffer[red_index:red_index + 3]
        clr_normalized = tuple([i / 255 for i in clr])
        return Color(rgb=clr_normalized)

    def __repr__(self) -> str:
        """
        Will create a grid of led color states. Each cell in the grid represents a pixel. Each pixel will display
        r, g, b or ., depending on the largest color. If the pixel is black, "." is used.
        
        :return: string representation of this canvas
        """
        result = ""
        for y in range(self.height):
            for x in range(self.width):
                result += self.__get_repr_color(self.get_color(x, y))
            result += "\n"
        return result

    def get_buffer_for_arduino(self) -> bytearray:
        """
        This method can be used to retrieve the internal data buffer. Modifications will probably do weird shit. Mostly
        useful for pushing the data out to the arduino, who actually understands what all the numbers mean.
        
        :return: a bytearray with all color values
        """
        return self.data_buffer

    def set_font(self, path: str, size: int):
        """
        Load a font to be used for rendering all following text. (see draw_text)
        
        :param path: path to the font
        :param size: size of the font. For a 10x10 matrix, 13 is an acceptable, if rather large, choice.
        :return: nothing
        """
        self.font = Font(path, size)

    @staticmethod
    def __color_to_255_rgb(color: Color):
        """
        Convert a normalized color to byte colors from 0 to 255
        
        :param color: the color that should be converted 
        :return: a tuple containing all byte values in r, g, b order
        """
        return [int(round(i * 255)) for i in color.get_rgb()]

    def clear(self, color: Color = Color('black')):
        """
        Set all pixels to some color

        :param color: the color that should be applied
        """
        # convert from 0-1 normalized to 0-255
        rgb_color = self.__color_to_255_rgb(color)

        # should be faster than manually zeroing all entries
        if rgb_color == [0, 0, 0]:
            self.data_buffer = bytearray(self.buffer_length)
        # write the color code to all leds
        else:
            for i in range(self.led_count):
                self.data_buffer[3 * i:3 * i + 3] = rgb_color

    def draw_pixel(self, x: int, y: int, color: Color):
        """
        Set a pixel to a color. Most basic canvas function.

        :param x: x position of pixel; counted from zero beginning on the left, must be smaller than the canvas width
        :param y: y position of pixel; y is zero for the top row of pixels, must be smaller than the canvas height
        :param color: the description of the color that should be set
        """

        # check input
        assert 0 <= x < self.width, "x coordinate out of valid range! " + str(x)
        assert 0 <= y < self.height, "y coordinate out of valid range! " + str(y)

        # update data in position
        self.__write_color_at(x, y, color)

    def draw_text(self, text: str, x: int, y: int, color: Color, ignore_height_warning=False):
        """
        Draw text on the canvas. Rendering over the borders is cut off, so you do not need boundary checking.
        
        :param text: the text to be rendered 
        :param x: the top-left starting position of the text
        :param y: the top-left starting position of the text
        :param color: color of the text
        :param ignore_height_warning: if true, no warning will be logged that the font does not fit into the available
            height. if false, a warning will be printed in the log on each such occasion
        :return: nothing
        """
        assert self.font is not None, "No font loaded! Use set_font(path, size)!"

        rendered_text = self.font.render_text(text)

        if rendered_text.height > self.height:
            self.logger.warning("Warning: The rendered text is higher than the canvas")

        # calculate appropriate render width (draw at most to canvas border, or (if smaller) to text border)
        available_horizontal_space = self.width - x
        if rendered_text.width < available_horizontal_space:
            render_width = rendered_text.width
        else:
            render_width = available_horizontal_space

        # calculate appropriate render height
        available_vertical_space = self.height - y
        if rendered_text.height < available_vertical_space:
            render_height = rendered_text.height
        else:
            render_height = available_vertical_space

        # render text to our canvas
        font_x = 0
        font_y = 0
        for canvas_x in range(x, render_width):
            for canvas_y in range(y, render_height):
                pixel_enabled = rendered_text.is_enabled(font_x, font_y)
                if pixel_enabled:
                    self.draw_pixel(canvas_x, canvas_y, color)
                font_y += 1
            font_x += 1
            font_y = 0

    def draw_rect(self, x: int, y: int, width: int, height: int, color: Color):
        """
        
        :param x: x position of pixel; counted from zero beginning on the left, must be smaller than the canvas width
        :param y: y position of pixel; y is zero for the top row of pixels, must be smaller than the canvas height
        :param width: how wide the rectangle should be.
        :param height: how high the rectangle should be
        :param color: the color the rectangle should have
        :return: nothing
        """
        for _x in range(x, x + width):
            for _y in range(y, y + height):
                self.draw_pixel(_x, _y, color)

    def draw_line(self, x_start: int, y_start: int, x_end: int, y_end: int, color: Color):
        """
        An implementation of bresenhams line drawing algorithm. Draws a line from <x_start, y_start> to <x_end, y_end>
        in the given color.

        :param x_start: x position where the line should start
        :param y_start: y position where the line should end
        :param x_end: x position where the line should start
        :param y_end: y position where the line should end
        :param color: color the line should be drawn in
        :return: nothing
        """
        # ensure start is smaller than end
        if y_start > y_end:
            y_start, y_end = y_end, y_start
        if x_start > x_end:
            x_start, x_end = x_end, x_start

        delta_x = x_end - x_start

        # handle vertical lines
        if delta_x == 0:
            for y in range(y_start, y_end):
                self.draw_pixel(x_start, y, color)
        else:
            delta_y = y_end - y_start
            delta_error = abs(delta_y / delta_x)
            error = delta_error - 0.5
            y = y_start

            for x in range(x_start, x_end + 1):
                self.draw_pixel(x, y, color)
                error += delta_error
                if error >= 0.5:
                    y += 1
                    error -= 1
