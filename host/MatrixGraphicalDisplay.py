import logging
import threading
from tkinter import Tk, Scale, Button
from tkinter import Canvas as TkCanvas
from typing import Callable

from helpers.Color import Color

import Canvas
from helpers.custom_atexit import CustomAtExit


class MatrixGraphicalDisplay:
    def __init__(self, matrix_width, matrix_height, matrix_rotation, restart_current_script_function: Callable):
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
        self.tk_root.geometry("{}x{}".format(self.width, self.height + 150))
        self.tk_root.title = "Matrix test window"
        self.tk_canvas = TkCanvas(self.tk_root)
        self.tk_canvas.pack()
        self.tk_fps_slider = Scale(self.tk_root, orient="horizontal", from_=1, to=120)
        self.tk_fps_slider.set(24)
        self.tk_fps_slider.pack()
        self.tk_restart_script_button = Button(self.tk_root, text="Restart current script", command=restart_current_script_function)
        self.tk_restart_script_button.pack()


        self.tk_root.protocol("WM_DELETE_WINDOW", self.on_closing)

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

    def on_closing(self):
        self.__destroy_flag.set()

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

    def get_requested_fps(self):
        return self.tk_fps_slider.get()

    def update_with_canvas(self, canvas: Canvas) -> bool:
        """
        Update the window display. Call from main thread only.

        :param canvas: the canvas to be displayed
        :return: False if the canvas has been destroyed
        """
        if self.__destroy_flag.is_set():
            self.tk_root.destroy()
            CustomAtExit().trigger()
            return False

        for x in range(self.matrix_width):
            for y in range(self.matrix_height):
                color = "#{:02X}{:02X}{:02X}".format(*canvas.get_color_rgb(x, y))
                old_rectangle_color = self.rectangles[x][y][1]

                if old_rectangle_color != color:
                    self.tk_canvas.itemconfigure(self.rectangles[x][y][0], fill=color)
                    self.rectangles[x][y][1] = color

        self.tk_root.update()

        return True
