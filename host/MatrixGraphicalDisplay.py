from helpers.Color import Color

import Canvas
from helpers.graphics import *


class MatrixGraphicalDisplay:
    def __init__(self, matrix_width = 10, matrix_height = 10):
        # create new window
        self.width = matrix_width * 20
        self.height = matrix_height * 20
        self.win = GraphWin("Matrix test window", width = self.width, height = self.height, autoflush=False)

        # translate coordinate system to matrix dimensions
        self.win.setCoords(0, matrix_height, matrix_width, 0)

        # store matrix dimensions
        self.matrix_width = matrix_width
        self.matrix_height = matrix_height

        # led display width
        self.led_width = self.width / self.matrix_width
        self.led_height = self.height / self.matrix_height

    @staticmethod
    def __convert_color(color: Color):
        rgb_255 = [int(round(i * 255)) for i in color.get_rgb()]
        return color_rgb(*rgb_255)

    def update_with_canvas(self, canvas: Canvas):
        """
        Update the window display. Call from main thread only.

        :param canvas: the canvas to be displayed
        :return: nothing
        """
        for x in range(self.matrix_width):
            for y in range(self.matrix_height):
                led_rect = Rectangle(Point(x, y), Point(x + 1, y + 1))
                color_tuple = canvas.get_color(x, y).get_rgb()
                led_rect.setFill(color_rgb(*color_tuple))
                if not self.win.isClosed():
                    led_rect.draw(self.win)

        if not self.win.isClosed():
            self.win.update()

    def get_key(self):
        """
        Get pressed key. Can be used to block until user input
        :return: key as gotten from graphics.py
        """
        return self.win.getKey()
