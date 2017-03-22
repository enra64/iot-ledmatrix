from fonts import Font


class Canvas:
    """
    The canvas class is designed to be a rather loosely-operated class, only drawing to its internal representation. The
    current canvas, however, can be exported using get_buffer and then be directly exported using the matserial.py functions
    """

    def __init__(self, width, height):
        """
        Initialise a new canvas object. A canvas can be used to produce data readable by the arduino by doing the desired
        operations, and the calling get_buffer.

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

    def get_pixel_index(self, x, y):
        # dont ask
        return self.__get_pixel_index(x, y)

    def __get_pixel_index(self, x, y):
        """convert an xy coordinate into an index that can be used to access our buffer. function may be made swappable
        to support different led chaining methods

        Currently, the chaining is assumed to be in a zig-zag, as follows:
        +----+----+----+----+----+----+----+----+----+----+
        | 99 | 98 | 97 | 96 | 95 | 94 | 93 | 92 | 91 | 90 |
        +----+----+----+----+----+----+----+----+----+----+
        | 80 | 81 | 82 | 83 | 84 | 85 | 86 | 87 | 88 | 89 |
        +----+----+----+----+----+----+----+----+----+----+
        | 79 | 78 | 77 | 76 | 75 | 74 | 73 | 72 | 71 | 70 |
        +----+----+----+----+----+----+----+----+----+----+
        | 60 | 61 | 62 | 63 | 64 | 65 | 66 | 67 | 68 | 69 |
        +----+----+----+----+----+----+----+----+----+----+
        | 59 | 58 | 57 | 56 | 55 | 54 | 53 | 52 | 51 | 50 |
        +----+----+----+----+----+----+----+----+----+----+
        | 40 | 41 | 42 | 43 | 44 | 45 | 46 | 47 | 48 | 49 |
        +----+----+----+----+----+----+----+----+----+----+
        | 39 | 38 | 37 | 36 | 35 | 34 | 33 | 32 | 31 | 30 |
        +----+----+----+----+----+----+----+----+----+----+
        | 20 | 21 | 22 | 23 | 24 | 25 | 26 | 27 | 28 | 29 |
        +----+----+----+----+----+----+----+----+----+----+
        | 19 | 18 | 17 | 16 | 15 | 14 | 13 | 12 | 11 | 10 |
        +----+----+----+----+----+----+----+----+----+----+
        | 0  | 1  | 2  | 3  | 4  | 5  | 6  | 7  | 8  | 9  |
        +----+----+----+----+----+----+----+----+----+----+ """
        # this variable will have the final index
        index = 0

        # have fun
        if y % 2 == 1:
            # odd rows are left-to-right
            index += x

            # y is [0, height - 1], multiply with width to represent the number of leds we need to go to get to the row
            index += (self.height - 1 - y) * self.width
        else:
            index += (self.height - y) * self.width
            index -= (x + 1)

        return index

    def __get_color_pixel_index(self, x, y, color):
        return self.get_pixel_index(x, y) * 3 + color

    def __repr__(self):
        """Will print an '#' for each pixel that is red > 0, and a '.' elsewhere"""
        result = ""
        for y in range(self.height):
            for x in range(self.width):
                if self.data_buffer[self.__get_color_pixel_index(x, y, 0)] > 0:
                    result += "#"
                else:
                    result += "."
            result += "\n"
        return result

    def get_buffer(self):
        return self.data_buffer

    def set_font(self, path: str, size: int):
        """Load a font to be used for rendering text"""
        self.font = Font(path, size)

    def clear(self, r = 0, g = 0, b = 0):
        """Set all pixels to some color"""
        if r == 0 and g == 0 and b == 0:
            self.data_buffer = bytearray(self.buffer_length)
        else:
            for i in range(self.led_count):
                self.data_buffer[3 * i:3 * i + 3] = [r, g, b]

    def draw_pixel(self, x: int, y: int, r: int, g: int, b: int):
        """
        Set a pixel to a color. Most basic canvas function.

        :param x: x position of pixel; counted from zero beginning on the left, must be smaller than the canvas width
        :param y: y position of pixel; y is zero for the top row of pixels, must be smaller than the canvas height
        :param r: red value from 0 to 255
        :param g: green value from 0 to 255
        :param b: blue value from 0 to 255
        """

        # check input
        assert 0 <= x < self.width, "x coordinate out of valid range! " + str(x)
        assert 0 <= y < self.height, "y coordinate out of valid range! " + str(y)
        assert 0 <= r < 256, "r out of valid range [0, 255] " + str(r)
        assert 0 <= g < 256, "g out of valid range [0, 255] " + str(g)
        assert 0 <= b < 256, "b out of valid range [0, 255] " + str(b)

        # translate position to index
        index = self.__get_color_pixel_index(x, y, 0)

        # update data in position
        self.data_buffer[index + 0] = r
        self.data_buffer[index + 1] = g
        self.data_buffer[index + 2] = b

    def draw_text(self, text, x, y, r, g, b):
        """Rather unoptimized function to draw fonts onto the canvas. Feel free to optimize"""
        assert self.font != None, "No font loaded! Use set_font(path, size)!"

        rendered_text = self.font.render_text(text)

        if rendered_text.height > self.height:
            print("Warning: The rendered text is higher than the canvas")

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
                    self.draw_pixel(canvas_x, canvas_y, r, g, b)
                font_y += 1
            font_x += 1
            font_y = 0

    def draw_rect(self, x, y, width, height, r, g, b):
        for _x in range(x, x + width):
            for _y in range(y, y + height):
                self.draw_pixel(_x, _y, r, g, b)

    def draw_line(self, x_start: int, y_start: int, x_end: int, y_end: int, r: int, g: int, b: int):
        """
        good ole bresenham

        :param x_start:
        :param y_start:
        :param x_end:
        :param y_end: must be larger than
        :param r:
        :param g:
        :param b:
        :return:
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
                self.draw_pixel(x_start, y, r, g, b)
        else:
            delta_y = y_end - y_start
            delta_error = abs(delta_y / delta_x)
            error = delta_error - 0.5
            y = y_start

            for x in range(x_start, x_end + 1):
                self.draw_pixel(x, y, r, g, b)
                error += delta_error
                if error >= 0.5:
                    y += 1
                    error -= 1
