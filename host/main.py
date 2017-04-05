import getopt
import sys

import logging

import tests
from custom_atexit import CustomAtExit
from Manager import Manager
from matrix_serial import MatrixSerial, get_connected_arduinos, guess_arduino


def test_serial():
    ser = MatrixSerial("/dev/ttyUSB0", 100, connect=True)
    tests.red_display_test(ser)
    tests.test_canvas_draw_pixel_line(ser)


def test():
    tests.test_script_handler_exception_handling()
    tests.test_invalid_script_name()
    tests.test_canvas_pixel_line()
    tests.test_pixel_index_conversion()
    tests.test_canvas_rect()
    tests.test_canvas_line()
    tests.test_script_handler()
    tests.test_canvas_font()
    tests.test_broadcast_receiver()
    tests.test_broadcast_receiver_and_server()


def print_help():
    print("-h")
    print("--help                           this help")
    print("--getports                       list of comports. might include arduinos")
    print("--test-with-serial               run only tests testing serial connection")
    print("--test                           run all tests but those requiring an arduino + leds be connected")
    print()
    print("--errors-to-console              divert errors to console instead of logfile")
    print("--set-arduino-port=              set the port the arduino is connected on manually, like /dev/ttyUSB0. if not given, port will be guessed.")
    print("--name=                          set the name the ledmatrix will advertise itself as")
    print("--width=                         define horizontal number of leds in matrix")
    print("--height=                        define vertical number of leds in matrix")
    print("--data-port=                     set the data port the ledmatrix server will use")
    print("--discovery-port=                set the discovery port the led matrix discovery server will use")
    print("--loglevel=                      set python logging loglevel")
    print("--disable-arduino-connection     disable arduino connection. mostly useful for debugging without an arduino")

if __name__ == "__main__":
    # try and get the script parameters
    try:
        options, arguments = getopt.getopt(
            sys.argv[1:],
            "h",
            [
                "help",
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
                "errors-to-console"
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
    log_to_file = True
    log_level = logging.INFO
    run = True

    if len(options) > 0:
        for option, argument in options:
            if option == "-h" or option == "--help":
                print_help()
                run = False
            elif option == "--test":
                test()
                run = False
            elif option == "--test-serial":
                test_serial()
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
            elif option == "--errors-to-console":
                log_to_file = False

    if matrix_connect_to_arduino and matrix_port is None:
        matrix_port = guess_arduino()

    logger = logging.getLogger("main")

    # set logging level
    if log_to_file:
        logging.basicConfig(filename='ledmatrix.log', level=log_level, datefmt='%d.%m.%Y@%H:%M:%S', format='%(asctime)s: %(levelname)s: %(message)s')
    else:
        logging.basicConfig(level=log_level, datefmt='%d.%m.%Y@%H:%M:%S', format='%(asctime)s: %(levelname)s: %(message)s')
    if run:
        manager = Manager(
            matrix_port,
            115200,
            matrix_width,
            matrix_height,
            matrix_data_port,
            matrix_name,
            matrix_discovery_port,
            matrix_connect_to_arduino)
        try:
            manager.start()
            manager.load_script("gameoflife")
            # wait for exit to be able to catch exceptions
            manager.join()
        except KeyboardInterrupt:
            logger.info("shutting down on manual command")

            # force CustomAtExit to ignore the system atexit that it has registered for itself so it does
            # not trigger twice
            CustomAtExit().disarm_system_atexit()

            # will also stop the manager
            CustomAtExit().trigger()

