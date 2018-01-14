import logging
import threading
from tkinter import Tk
from tkinter import Canvas as TkCanvas

from helpers.Color import Color

import Canvas


class MatrixGraphicalDisplay:
    def __init__(self, matrix_width, matrix_height, matrix_rotation):
        """
        Create a new matrix gui

        :param matrix_width: number of leds in x dimension
        :param matrix_height: number of leds in y dimension
        :param matrix_rotation: rotation of matrix. the gui cannot handle this. a warning will be generated if you use
                                anything but zero to avoid spending two hours on finding this
        """
        if matrix_rotation != 0:
            self.logger = logging.getLogger("MatrixGraphicalDisplay")
            self.logger.error("the matrix gui cannot display rotation. you do not want to try this.")


        # create new window
        self.width = matrix_width * 20
        self.height = matrix_height * 20
        self.tk_root = Tk()
        self.tk_root.geometry("{}x{}".format(self.width, self.height))
        self.tk_root.title = "Matrix test window"
        self.tk_canvas = TkCanvas(self.tk_root)
        self.tk_canvas.pack()

        # store matrix dimensions
        self.matrix_width = matrix_width
        self.matrix_height = matrix_height

        # led display width
        self.led_width = self.width / self.matrix_width
        self.led_height = self.height / self.matrix_height

        # pre-create the rectangles to be drawn
        self.rectangles = {}
        for x in range(self.matrix_width):
            if x not in self.rectangles:
                self.rectangles[x] = {}

            for y in range(self.matrix_height):
                self.rectangles[x][y] = [self.__create_rectangle(x, y), ""]

        # abort flag
        self.__destroy_flag = threading.Event()

    @staticmethod
    def __convert_color(color: Color) -> str:
        return color.get_hex_string()

    def destroy(self):
        """
        Will close this instance on the next update call

        :return: nothing
        """
        # set the abort flag
        self.__destroy_flag.set()

    def __create_rectangle(self, canvas_x: int, canvas_y: int) -> int:
        tk_x = canvas_x * 20
        tk_y = canvas_y * 20
        return self.tk_canvas.create_rectangle(tk_x, tk_y, tk_x + 20, tk_y + 20)

    def update_with_canvas(self, canvas: Canvas) -> bool:
        """
        Update the window display. Call from main thread only.

        :param canvas: the canvas to be displayed
        :return: False if the canvas has been destroyed
        """
        if self.__destroy_flag.is_set():
            self.tk_root.destroy()
            return False

        for x in range(self.matrix_width):
            for y in range(self.matrix_height):
                color = "#{:02X}{:02X}{:02X}".format(*canvas.get_color_rgb(x, y))
                old_rectangle_color = self.rectangles[x][y][1]

                if  old_rectangle_color != color:
                    self.tk_canvas.itemconfigure(self.rectangles[x][y][0], fill=color)
                    self.rectangles[x][y][1] = color

        self.tk_root.update()

        return True

    def get_key(self):
        """
        Get pressed key. Can be used to block until user input
        :return: key as gotten from graphics.py
        """
        return self.tk_canvas.getKey()
