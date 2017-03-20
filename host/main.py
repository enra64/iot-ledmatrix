import getopt
import sys

import iot_ledmatrix_component_tests
from manager import Manager
from matserial import MatrixSerial, get_connected_arduinos


def test_all():
    ser = MatrixSerial("/dev/ttyUSB0", 100, connect=True)

    iot_ledmatrix_component_tests.red_display_test(ser)
    iot_ledmatrix_component_tests.test_canvas_draw_pixel_line(ser)
    iot_ledmatrix_component_tests.test_canvas_pixel_line()
    iot_ledmatrix_component_tests.test_pixel_index_conversion()
    iot_ledmatrix_component_tests.test_canvas_rect()
    iot_ledmatrix_component_tests.test_canvas_line()
    iot_ledmatrix_component_tests.test_script_handler()
    iot_ledmatrix_component_tests.test_canvas_font()
    iot_ledmatrix_component_tests.test_broadcast_receiver()
    iot_ledmatrix_component_tests.test_broadcast_receiver_and_server()


def run():
    print("starting complete server")
    manager = Manager("/dev/ttyACM0", 115200, 10, 10, 55124, "arnes matrix")
    manager.start()
    manager.load_script("gameoflife")


if __name__ == "__main__":
    # test_all()
    options, arguments = getopt.getopt(sys.argv[1:], "h", ["test", "getports"])

    if len(options) > 0:
        for option, argument in options:
            if option == "-h":
                print("-h\t\t\tthis help")
                print("--getports\tlist of comports. might include arduinos")
                print("--test\t\trun tests")
            elif option == "--test":
                test_all()
            elif option == "--getports":
                arduinos = get_connected_arduinos()
                if len(arduinos) == 0:
                    print("no arduinos detected")
                else:
                    print("the following arduinos were detected")
                    print(get_connected_arduinos())
    else:
        run()
