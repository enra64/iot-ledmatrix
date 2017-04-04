import inspect
import time

from DiscoveryServer import DiscoveryServer
from Canvas import Canvas
from matrix_serial import MatrixSerial
from script_handling import ScriptHandler
from colour import Color

# begin serial test
from Server import Server


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
    c = Canvas(10, 10)
    for y in range(10):
        for x in range(10):
            print(str(x) + "," + str(y) + "=" + str(c.get_pixel_index(x, y)))


def test_canvas_line():
    print(inspect.currentframe().f_code.co_name)
    c = Canvas(10, 10)

    c.draw_line(0, 0, 9, 5, Color())
    print(repr(c))


def test_canvas_pixel_line():
    print(inspect.currentframe().f_code.co_name)
    c = Canvas(10, 10)

    blue = Color("blue")

    for i in range(c.width - 1, 0-1, -1):
        c.draw_pixel(9 - i, i, blue)
        print(repr(c))


def test_canvas_rect():
    print(inspect.currentframe().f_code.co_name)
    c = Canvas(10, 10)

    blue = Color("blue")

    c.draw_rect(2, 2, 4, 4, blue)
    print(repr(c))


def test_canvas_font():
    print(inspect.currentframe().f_code.co_name)
    c = Canvas(10, 10)
    c.set_font("helvetica.otf", 13)
    blue = Color("blue")
    c.draw_text("h", 0, 0, blue)
    print(repr(c))


def test_canvas_draw_pixel_line(serial):
    print(inspect.currentframe().f_code.co_name)
    c = Canvas(156, 1)

    blue = Color("blue")

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
        lambda client_id: print(client_id + " has connected"),
        lambda client_id: print(client_id + " has disconnected"),
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
    c = Canvas(10, 10)
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
    c = Canvas(10, 10)
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
