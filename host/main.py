import getopt
import sys

import logging

import iot_ledmatrix_component_tests
from manager import Manager
from matserial import MatrixSerial, get_connected_arduinos, guess_arduino


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

def print_help():
    print("-h\t\t\t\tthis help")
    print("--getports\t\tlist of comports. might include arduinos")
    print("--test\t\t\trun tests")
    print("--guess-arduino\tget the port we would try to use as an arduino")

if __name__ == "__main__":
    # test_all()
    try:
        options, arguments = getopt.getopt(
            sys.argv[1:],
            "h",
            [
                "test",
                "getports",
                "guess-arduino",
                "--set-port=",
                "--name=",
                "--width=",
                "--height=",
                "--data-port=",
                "--discovery-port=",
                "--loglevel="
            ]
        )
    except getopt.GetoptError:
        print_help()
        sys.exit(2)


    matrix_port = "/dev/ttyACM0"
    matrix_name = "ledmatrix"
    matrix_width = 10
    matrix_height = 10
    matrix_data_port = 55124
    matrix_discovery_port = 54123

    log_level = logging.INFO

    run = True

    if len(options) > 0:
        for option, argument in options:
            if option == "-h":
                print_help()
                run = False
            elif option == "--test":
                test_all()
                run = False
            elif option == "--getports":
                run = False
                arduinos = get_connected_arduinos()
                if len(arduinos) == 0:
                    print("no arduinos detected")
                else:
                    print("the following arduinos were detected")
                    for port in arduinos:
                        print(port)
            elif option == "--guess-arduino":
                matrix_port = guess_arduino()
            elif option == "--set-port":
                matrix_port = argument
            elif option == "--name":
                matrix_name = argument
            elif option == "--width":
                matrix_width = int(argument)
            elif option == "--height":
                matrix_height = int(argument)
            elif option == "--data-port":
                matrix_data_port = int(argument)
            elif option == "--discovery-port":
                matrix_discovery_port = int(argument)
            elif option == "--loglevel":
                log_level = getattr(logging, argument.upper(), None)

    # set logging level
    logging.basicConfig(filename='ledmatrix.log', level=log_level, datefmt='%d.%m.%Y %H:%M:%S')

    if run:
        logging.info("starting full operations")
        manager = Manager(matrix_port, 115200, matrix_width, matrix_height, matrix_data_port, matrix_name, matrix_discovery_port)
        manager.start()
        manager.load_script("gameoflife")
