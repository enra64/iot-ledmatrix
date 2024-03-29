import logging

import sys
from typing import Union

from zmq import ZMQError

from Canvas import Canvas
from DiscoveryServer import DiscoveryServer
from Server import Server
from ZeroconfDiscoveryServer import ZeroconfDiscoveryServer
from helpers.custom_atexit import CustomAtExit
from matrix_serial import MatrixSerial, MatrixReadException
from ScriptHandler import ScriptHandler


class Manager:
    """
    The Manager class provides a simple interface for using the matrix code.
    It correctly parametrizes the different modules, has a unified start() and
    stop() function, and can join the module threads when necessary.
    """

    def script_load_request_handler(self, script_name: str, source_id):
        """start a new script"""
        self.script_handler.start_script(script_name, source_id)

    def script_data_handler(self, script_data, source_id):
        """forward data sent from a client to the currently running script"""
        self.script_handler.on_data(script_data, source_id)

    def on_draw_cycle_finished(self):
        """update the matrix after every draw cycle"""
        try:
            self.matrix_serial.update(self.canvas.get_buffer_for_arduino())
        except MatrixReadException:
            self.logger.warning("START Restarting connection to arduino...")
            self.matrix_serial.stop()
            self.matrix_serial.connect()
            self.logger.warning("FINISH Restarting connection to arduino...")

    def join(self):
        """join all started threads"""
        if not self.disable_discovery:
            self.discovery_server.join()
        self.server.join()
        self.script_handler.join()

    def start(self):
        """starts all required modules"""
        self.matrix_serial.connect()
        if self.disable_discovery:
            self.logger.info("Skipping discovery start")
        else:
            self.discovery_server.start()
            self.zeroconf_discovery_server.start_advertising()

        try:
            self.server.start()
            self.logger.info("manager started threads")
        except ZMQError as e:
            self.logger.warning("ZMQError occurred: {}".format(e.strerror))

    def stop(self):
        """gracefully stop all modules"""
        self.script_handler.stop_current_script()
        self.matrix_serial.stop()
        if not self.disable_discovery:
            self.discovery_server.stop()
            self.zeroconf_discovery_server.stop_advertising()
        self.server.stop()
        if self.gui is not None:
            self.gui.destroy()
            self.gui = None
        self.logger.info("shut down")
        self.join()
        sys.exit(0)

    def load_script(self, script):
        """load specific script"""
        self.script_handler.start_script(script, "hardcoded")

    def __init__(
            self,
            arduino_interface,
            arduino_baud,
            matrix_width,
            matrix_height,
            data_port: int,
            server_name: str,
            discovery_port: int,
            disable_discovery: bool,
            enable_arduino_connection: bool,
            enable_graphical_display: bool,
            matrix_rotation: int,
            keepalive: bool
    ):
        """
        Initializes instances of: MatrixSerial, BroadcastReceiver, Server, Canvas and ScriptHandler. Registers 
        manager.stop for a shutdown hook.
        
        :param arduino_interface: the interface at which the arduino is to be found, like /dev/ttyUSB0 
        :param arduino_baud: arduino baud. most likely 115200
        :param matrix_width: width of the matrix
        :param matrix_height: height of the matrix
        :param data_port: the data port at which the server should be listening
        :param server_name: name of the server as advertised to the clients
        :param discovery_port: the discovery port at which the DiscoveryServer is listening for discovery requests
        :param enable_arduino_connection: if True, MatrixSerial will attempt to connect to the arduino
            if False, no connection attempt is made; useful for debugging.
        :param enable_graphical_display: if True, MatrixSerial will attempt to create a tkinter window with the matrix graphics. there must
            be a main thread calling update_gui every now and then to update the gui; if that is not done, the window is not updated; if it
            is not called from the main thread, an exception will be logged.
        :param matrix_rotation: clockwise. rotates the matrix, so that you can turn the physical item. 0/90/180/270 are valid.
        :param keepalive: if True, crashed CustomScripts will be restarted
        """
        """initializes all required modules without starting any of them."""

        self.logger = logging.getLogger("manager")

        # log that the manager will now attempt to initialize
        self.logger.info("beginning initialization routines. pray to the gods...")

        # matrix serial connects to the arduino and sends data to it
        self.matrix_serial = MatrixSerial(
            arduino_interface,
            matrix_width * matrix_height,
            arduino_baud,
            connect=False,  # we shall connect in start()
            enable_arduino_connection=enable_arduino_connection
        )

        # the discovery server manages everything related to server discovery for clients
        self.discovery_server = DiscoveryServer(
            discovery_port,
            data_port,
            server_name,
            matrix_height=matrix_height,
            matrix_width=matrix_width
        )

        # the zeroconf discovery server is the future discovery system
        self.zeroconf_discovery_server = ZeroconfDiscoveryServer(
            server_name,
            data_port,
            matrix_width=matrix_width,
            matrix_height=matrix_height
        )

        # the server communicates with the clients
        self.server = Server(
            self.script_load_request_handler,
            self.script_data_handler,
            (matrix_width, matrix_height),
            data_port
        )

        # canvas instance whose back buffer is sent to the arduino
        self.canvas = Canvas(
            matrix_width,
            matrix_height,
            matrix_rotation
        )

        # script handler starts and runs custom scripts
        self.script_handler = ScriptHandler(
            self.canvas,
            self.on_draw_cycle_finished,
            self.server.send_object,
            self.server.send_object_all,
            self.server.get_client_list,
            keepalive
        )

        # give the server the functions to call when clients dis/connect
        self.server.on_client_connected = self.script_handler.on_client_connected
        self.server.on_client_disconnected = self.script_handler.on_client_disconnected

        self.disable_discovery = disable_discovery
        self.enable_graphical_display = enable_graphical_display

        self.gui = None
        if self.enable_graphical_display:
            try:
                from MatrixGraphicalDisplay import MatrixGraphicalDisplay
                self.gui = MatrixGraphicalDisplay(matrix_width, matrix_height, matrix_rotation,
                                                  self.script_handler.restart_current_script)
            except ImportError as e:
                self.logger.warning("failing to import GUI, disabling it ({})".format(str(e)))
                self.enable_graphical_display = False
                self.gui = None

        # register the manager stop (stop all previously started parts) for exit execution
        CustomAtExit().register(self.stop)

        # log that the manager survived init
        self.logger.info("survived initialization")

    def get_gui_requested_fps(self):
        return self.gui.get_requested_fps()

    def update_gui(self) -> bool:
        """
        Update the gui, and return false if the gui must not be updated anymore
        :return:
        """
        if self.gui is not None:
            return self.gui.update_with_canvas(self.canvas)
        else:
            return False
