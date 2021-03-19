import getopt
import logging
import os
import sys
from time import sleep

import tests
from Manager import Manager
from helpers.custom_atexit import CustomAtExit
from matrix_serial import MatrixSerial, get_connected_arduinos, guess_arduino


def test_serial():
    ser = MatrixSerial("/dev/ttyUSB0", 100, connect=True)
    tests.red_display_test(ser)
    tests.test_canvas_draw_pixel_line(ser)


def test():
    tests.test_gui_canvas_display_by_line()
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
    print("--set-arduino-port=              set the port the arduino is connected on manually, like /dev/ttyUSB0. if "
          "not given, port will be guessed.")
    print("--name=                          set the name the ledmatrix will advertise itself as")
    print("--width=                         define horizontal number of leds in matrix")
    print("--height=                        define vertical number of leds in matrix")
    print("--data-port=                     set the data port the ledmatrix server will use")
    print("--discovery-port=                set the discovery port the led matrix discovery server will use")
    print("--disable-discovery              disable internal discovery methods in case you want to use other means")
    print("--loglevel=                      set python logging loglevel")
    print("--disable-arduino-connection     disable arduino connection. mostly useful for debugging without an arduino")
    print("--logfile=                       set log file location")
    print("--start-script=                  set starting script, defaults to 'gameoflife'")
    print("--enable-gui                     enable a simplistic gui displaying what the matrix should currently show. "
          "combine with --disable-arduino-connection for easy testing. will fuck up stopping. recommended for "
          "debugging only")
    print("--rotation=                      set matrix rotation amount. clockwise. valid are 0/90/180/270.")
    print("--keepalive                      restart crashed CustomScripts")
    print("--shutdown-pin=                  set a BCM pin number that will shut down the RPi on a rising edge")


if __name__ == "__main__":
    # change working directory to main.py location to avoid confusion with scripts folder
    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    os.chdir(dname)

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
                "errors-to-console",
                "logfile=",
                "disable-discovery",
                "start-script=",
                "enable-gui",
                "rotation=",
                "keepalive",
                "shutdown-pin="
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
    log_location = "ledmatrix.log"
    run = True
    start_script = "gameoflife"
    enable_graphical_display = False
    matrix_rotation = 0
    keepalive = False
    disable_discovery = False
    shutdown_pin = None

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
            elif option == "--shutdown-pin":
                shutdown_pin = argument
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
            elif option == "--disable-discovery":
                disable_discovery = True
            elif option == "--loglevel":
                log_level = getattr(logging, argument.upper(), None)
            elif option == "--disable-arduino-connection":
                matrix_connect_to_arduino = False
            elif option == "--errors-to-console":
                log_to_file = False
            elif option == "--logfile":
                log_location = argument
            elif option == "--start-script":
                start_script = argument
            elif option == "--keepalive":
                keepalive = True
            elif option == "--enable-gui":
                enable_graphical_display = True
            elif option == "--rotation":
                matrix_rotation = int(argument)
            else:
                print("unrecognized option:" + option)

    if matrix_connect_to_arduino and matrix_port is None:
        matrix_port = guess_arduino()

        if matrix_port is None:
            logging.warning(
                "port was not specified, and arduino was not disabled, but the port guesser did not find a port. ABORT!")
            sys.exit(1)

    logger = logging.getLogger("main")

    # set logging level
    if log_to_file:
        logging.basicConfig(filename=log_location, level=log_level, datefmt='%d.%m.%Y@%H:%M:%S',
                            format='%(asctime)s: %(levelname)s: %(message)s')
    else:
        logging.basicConfig(level=log_level, datefmt='%d.%m.%Y@%H:%M:%S',
                            format='%(asctime)s: %(levelname)s: %(message)s')
    if run:
        manager = Manager(
            matrix_port,
            115200,
            matrix_width,
            matrix_height,
            matrix_data_port,
            matrix_name,
            matrix_discovery_port,
            disable_discovery,
            matrix_connect_to_arduino,
            enable_graphical_display,
            matrix_rotation,
            keepalive,
            shutdown_pin
        )
        try:
            manager.start()
            manager.load_script(start_script)
            # enable gui
            if enable_graphical_display:
                while manager.update_gui():
                    sleep(1 / manager.get_gui_requested_fps())
            # wait for exit to be able to catch exceptions
            manager.join()

        except KeyboardInterrupt:
            logger.info("shutting down control system due to manual command")

            # force CustomAtExit to ignore the system atexit that it has registered for itself so it does
            # not trigger twice
            CustomAtExit().disarm_system_atexit()

            # will also stop the manager
            CustomAtExit().trigger()
