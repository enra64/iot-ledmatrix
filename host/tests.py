import inspect
import time

from Canvas import Canvas
from DiscoveryServer import DiscoveryServer
from ScriptHandler import ScriptHandler
# begin serial test
from Server import Server
from helpers.Color import Color
from matrix_serial import MatrixSerial


def red_display_test(serial: MatrixSerial):
    """draw red to all pixels without using canvas; mostly a MatrixSerial test"""
    print(inspect.currentframe().f_code.co_name)

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
    print(inspect.currentframe().f_code.co_name)
    c = Canvas(10, 10, 0)
    for y in range(10):
        for x in range(10):
            print(str(x) + "," + str(y) + "=" + str(c.get_pixel_index(x, y)))


def test_canvas_line():
    print(inspect.currentframe().f_code.co_name)
    c = Canvas(10, 10, 0)

    c.draw_line(0, 0, 9, 5, Color())
    print(repr(c))


def test_canvas_pixel_line():
    print(inspect.currentframe().f_code.co_name)
    c = Canvas(10, 10, 0)

    blue = Color(0, 0, 255)

    for i in range(c.width - 1, 0-1, -1):
        c.draw_pixel(9 - i, i, blue)
        print(repr(c))


def test_canvas_rect():
    print(inspect.currentframe().f_code.co_name)
    c = Canvas(10, 10, 0)

    blue = Color(0, 0, 255)

    c.draw_rect(2, 2, 4, 4, blue)
    print(repr(c))


def test_canvas_font():
    print(inspect.currentframe().f_code.co_name)
    c = Canvas(10, 10, 0)
    c.set_font("helvetica.otf", 13)
    blue = Color(0, 0, 255)
    c.draw_text("h", 0, 0, blue)
    print(repr(c))


def test_canvas_draw_pixel_line(serial):
    print(inspect.currentframe().f_code.co_name)
    c = Canvas(156, 1, 0)

    blue = Color(0, 0, 255)

    while True:
        for i in range(c.width):
            c.draw_pixel(i, 0, blue)
            serial.update(c.get_buffer_for_arduino())


def test_broadcast_receiver():
    print(inspect.currentframe().f_code.co_name)
    receiver = DiscoveryServer(name="test_broadcast_receiver", matrix_height=10, matrix_width=10)
    receiver.start()
    time.sleep(200)
    receiver.stop()


def test_broadcast_receiver_and_server():
    print(inspect.currentframe().f_code.co_name)
    receiver = DiscoveryServer(name="test_broadcast_receiver_and_server", matrix_height=10, matrix_width=10)
    receiver.start()

    server = Server(
        lambda data, source: print("got " + data + " from " + str(source)),
        lambda data, source: print("got " + data + " from " + str(source)),
        local_data_port=receiver.get_advertised_data_port(),
        matrix_dimensions=(10, 10)
    )
    server.start()

    time.sleep(200)
    receiver.stop()
    server.stop()


def __return_list():
    return []


def test_invalid_script_name():
    print(inspect.currentframe().f_code.co_name)
    print("should print or have printed an error about \"invalid-script**dafsdf\" not existing...")
    c = Canvas(10, 10, 0)
    handler = ScriptHandler(
        c,
        lambda: print("draw cycle finished"),
        lambda data, client_id: print("sending " + data + " to " + client_id),
        lambda data: print("sending " + data + " to all"),
        __return_list()
    )

    handler.start_script("invalid-script**dafsdf", "test_script_handler")


def test_script_handler():
    print(inspect.currentframe().f_code.co_name)
    c = Canvas(10, 10, 0)
    handler = ScriptHandler(
        c,
        lambda: print("draw cycle finished"),
        lambda data, client_id: print("sending " + data + " to " + client_id),
        lambda data: print("sending " + data + " to all"),
        __return_list
    )

    handler.start_script("_CustomScriptTester", "test_script_handler")
    time.sleep(.5)
    handler.stop_current_script()


def test_gui_canvas_display_by_line():
    print(inspect.currentframe().f_code.co_name)
    print("should print blue line bottom left to top right")
    try:
        from MatrixGraphicalDisplay import MatrixGraphicalDisplay

        c = Canvas(15, 10, 0)
        gui = MatrixGraphicalDisplay(15, 10, 0)
        blue = Color(0, 0, 255)

        for i in range(c.width - 1, 0-1 + (c.width - c.height), -1):
            c.draw_pixel(c.width - 1 - i, i - (c.width - c.height), blue)
            gui.update_with_canvas(c)

        time.sleep(.4)

    except ImportError:
        print("could not import tkinter, probably")


def test_gui_canvas_display_pixel_counter_up():
    print(inspect.currentframe().f_code.co_name)
    print("should print blue line from pixel 0 to 41")
    try:
        from MatrixGraphicalDisplay import MatrixGraphicalDisplay

        c = Canvas(42, 1, 0)
        gui = MatrixGraphicalDisplay(42, 1, 0, test_gui_canvas_display_by_line)
        blue = Color(0, 0, 255)

        for i in range(42):
            c.draw_pixel(i, 0, blue)
            gui.update_with_canvas(c)

            time.sleep(0.6)

    except ImportError:
        print("could not import tkinter, probably")


def test_script_handler_exception_handling():
    print(inspect.currentframe().f_code.co_name)
    print("various exceptions in the code are commented to avoid early aborts")
    print("the following should only log the exceptions and abort executing the script, not die.\n")
    c = Canvas(10, 10, 0)
    handler = ScriptHandler(
        c,
        lambda: print("draw cycle finished"),
        lambda data, client_id: print("sending " + data + " to " + client_id),
        lambda data: print("sending " + data + " to all"),
        __return_list
    )

    handler.start_script("_CustomScriptThrowExceptionsEverywhere", "test_script_handler")
