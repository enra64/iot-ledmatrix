import time

from matgraphics import Canvas
from matserial import MatrixSerial
from script_handler import ScriptHandler

# begin serial test

def red_display_test(serial: MatrixSerial):
    """draw red to all pixels without using canvas; mostly a MatrixSerial test"""
    # "red" color specification
    r = [255, 0, 0]

    # construct test data showing red on all leds
    red_test_data = bytearray()
    for i in range(0, serial.get_led_count()):
        red_test_data.extend(r)

    for i in range(250):
        serial.update(red_test_data)


# begin canvas tests


def test_pixel_index_conversion():
    c = Canvas(10, 10)
    for y in range(10):
        for x in range(10):
            print(str(x) + "," + str(y) + "=" + str(c.get_pixel_index(x, y)))


def test_canvas_line():
    c = Canvas(10, 10)

    c.draw_line(0, 0, 9, 5, 255, 255, 255)
    print(repr(c))


def test_canvas_pixel_line():
    c = Canvas(10, 10)

    for i in range(c.width):
        c.draw_pixel(i, i, 255, 255, 255)
        print(repr(c))


def test_canvas_rect():
    c = Canvas(10, 10)

    c.draw_rect(2, 2, 4, 4, 255, 0, 0)
    print(repr(c))


def test_canvas_draw_pixel_line(serial):
    c = Canvas(156, 1)

    while True:
        for i in range(c.width):
            c.draw_pixel(i, 0, 255, 0, 0)
            serial.update(c.get_buffer())


# begin script handler testing
def test_script_handler():
    c = Canvas(10, 10)
    handler = ScriptHandler(c)

    handler.start_script("print_tester")
    time.sleep(.5)
    handler.stop_current_script()

    print("testing canvas outside of thread..., should be same as before")
    print(repr(c))
