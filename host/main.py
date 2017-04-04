import getopt
import sys

import logging

import iot_ledmatrix_component_tests
from custom_atexit import CustomAtExit
from Manager import Manager
from matrix_serial import MatrixSerial, get_connected_arduinos, guess_arduino


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
    print("-h                               this help")
    print("--getports                       list of comports. might include arduinos")
    print("--set-arduino-port=              set the port the arduino is connected on manually.")
    print("--name=                          set the name the ledmatrix will advertise itself as")
    print("--width=                         horizontal number of leds ")
    print("--height=                        vertical number of leds ")
    print("--data-port=                     set the data port this ledmatrix will use")
    print("--discovery-port=                set the discovery port this ledmatrix will use")
    print("--loglevel=                      set python logging loglevel")
    print("--disable-arduino-connection     disable arduino connection. mostly useful for debugging without an arduino")
    print("--no_custom_fragment_directory=  set custom directory for where to look for custom scripts requiring no custom fragment. be aware that changing this might cause some default fragments to not be found")
    print("--custom_fragment_directory=     set custom directory for where to look for custom scripts requiring a custom fragment. be aware that changing this might cause some default fragments to not be found.")

if __name__ == "__main__":
    # try and get the script parameters
    try:
        options, arguments = getopt.getopt(
            sys.argv[1:],
            "h",
            [
                "test",
                "getports",
                "set-arduino-port=",
                "name=",
                "width=",
                "height=",
                "data-port=",
                "discovery-port=",
                "loglevel=",
                "disable-arduino-connection",
                "no_custom_fragment_directory=",
                "custom_fragment_directory="
            ]
        )
    except getopt.GetoptError:
        print("bad arguments. look at this help:\n")
        print_help()
        sys.exit(2)

    # set default parameters
    matrix_port = None
    matrix_name = "ledmatrix"
    matrix_width = 10
    matrix_height = 10
    matrix_data_port = 55124
    matrix_discovery_port = 54123
    matrix_connect_to_arduino = True
    custom_fragment_directory = "scripts/custom_fragment_directory"
    no_custom_fragment_directory = "scripts/no_custom_fragment_directory"
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
            elif option == "--set-arduino-port":
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
            elif option == "--disable-arduino-connection":
                matrix_connect_to_arduino = False
            elif option == "custom_fragment_directory":
                custom_fragment_directory = argument
            elif option == "no_custom_fragment_directory":
                no_custom_fragment_directory = argument

    if matrix_connect_to_arduino and matrix_port is None:
        matrix_port = guess_arduino()

    # set logging level
    logging.basicConfig(filename='ledmatrix.log', level=log_level, datefmt='%d.%m.%Y@%H:%M:%S', format='%(asctime)s: %(levelname)s: %(message)s')

    if run:
        manager = Manager(
            matrix_port,
            115200,
            matrix_width,
            matrix_height,
            matrix_data_port,
            matrix_name,
            matrix_discovery_port,
            matrix_connect_to_arduino,
            custom_fragment_directory,
            no_custom_fragment_directory)
        try:
            manager.start()
            manager.load_script("gameoflife")
            # wait for exit to be able to catch exceptions
            manager.join()
        except KeyboardInterrupt:
            logging.info("shutting down on manual command")
            manager.stop()
            CustomAtExit().trigger()

