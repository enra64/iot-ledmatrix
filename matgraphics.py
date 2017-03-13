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

    def get_buffer(self):
        return self.data_buffer

    def set_font(self, path: str, size: int):
        """Load a font to be used for rendering text"""
        self.font = Font(path, size)

    def clear(self):
        """ Zero all colors to black """
        self.data_buffer = bytearray(self.buffer_length)

    def draw_pixel(self, x: int, y: int, r: int, g: int, b: int):
        """
        Set a pixel to a color. Most basic canvas function. The matrix is assumed to be set up in a zig-zag, as follows:
        1) the bottom left pixel is the pixel with index 0
        2) the bottom right pixel has index width-1, the pixel above that has index width
        3) the pixel above the bottom left pixel has index 2 * width - 1

        the lower area indices thus look like this for a 10x10 matrix:

        +----+----+----+----+----+----+----+----+----+----+
        | 20 | 21 | 22 | 23 | 24 | 25 | 26 | 27 | 28 | 29 |
        +----+----+----+----+----+----+----+----+----+----+
        | 19 | 18 | 17 | 16 | 15 | 14 | 13 | 12 | 11 | 10 |
        +----+----+----+----+----+----+----+----+----+----+
        | 0  | 1  | 2  | 3  | 4  | 5  | 6  | 7  | 8  | 9  |
        +----+----+----+----+----+----+----+----+----+----+

        :param x: x position of pixel; counted from zero beginning on the left, must be smaller than the canvas width
        :param y: y position of pixel; y is zero for the top row of pixels, must be smaller than the canvas height
        :param r: red value from 0 to 255
        :param g: green value from 0 to 255
        :param b: blue value from 0 to 255
        """

        # check input
        assert 0 < x < self.width, "x coordinate out of valid range!"
        assert 0 < y < self.height, "y coordinate out of valid range!"
        assert 0 < r < 256, "r out of valid range [0, 255]"
        assert 0 < g < 256, "g out of valid range [0, 255]"
        assert 0 < b < 256, "b out of valid range [0, 255]"

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

        self.data_buffer[index * 3 + 0] = r
        self.data_buffer[index * 3 + 0] = g
        self.data_buffer[index * 3 + 0] = b

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
                self.draw_pixel(rendered_text.get_pixel_index_inverted(font_x, font_y), canvas_x, canvas_y, r, g, b)
                canvas_y += 1
            canvas_x += 1

    def draw_rect(self, x, y, width, height, r, g, b):
        for _x in range(x, width - x):
            for _y in range(y, height - y):
                self.draw_pixel(_x, _y, r, g, b)
