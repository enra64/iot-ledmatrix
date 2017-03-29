import logging

from broadcast_receiver import BroadcastReceiver
from custom_atexit import CustomAtExit
from canvas import Canvas
from matserial import MatrixSerial
from script_handler import ScriptHandler
from zero_server import Server


class Manager:
    """
    The Manager class provides a simple interface for using the matrix code.
    It correctly parametrizes the different modules, has a unified start() and
    stop() function, and can join the modules where such action is necessary.
    """
    def script_load_request_handler(self, script_name: str, source_id):
        """start a new script"""
        self.script_handler.start_script(script_name, source_id)

    def script_data_handler(self, script_data, source_id):
        """forward data sent from a client to the currently running script"""
        self.script_handler.on_data(script_data, source_id)

    def on_draw_cycle_finished(self):
        """update the matrix after every draw cycle"""
        self.matrix_serial.update(self.canvas.get_buffer_for_arduino())

    def join(self):
        """join all started threads"""
        self.broadcast_receiver.join()
        self.server.join()
        self.script_handler.join()

    def start(self):
        """starts all required modules"""
        self.matrix_serial.connect()
        self.broadcast_receiver.start()
        self.server.start()

    def stop(self):
        "gracefully stop all modules"
        self.script_handler.stop_current_script()
        self.matrix_serial.stop()
        self.broadcast_receiver.stop()
        self.server.stop()
        logging.info("manager shut down")

    def load_script(self, script):
        """load specific script"""
        self.script_handler.start_script(script, "hardcoded")

    def __init__(self, arduino_interface, arduino_baud, matrix_width, matrix_height, data_port, server_name, discovery_port, enable_arduino_connection: bool):
        """
        Initializes instances of: MatrixSerial, BroadcastReceiver, Server, Canvas and ScriptHandler. Registers 
        manager.stop for a shutdown hook.
        
        :param arduino_interface: the interface at which the arduino is to be found, like /dev/ttyUSB0 
        :param arduino_baud: arduino baud. most likely 115200
        :param matrix_width: width of the matrix
        :param matrix_height: height of the matrix
        :param data_port: the data port at which the server should be listening
        :param server_name: name of the server as advertised to the clients
        :param discovery_port: the discovery port at which the BroadcastReceiver is listening for discovery requests
        :param enable_arduino_connection: if True, MatrixSerial will attempt to connect to the arduino
            if False, no connection attempt is made; useful for debugging.
        """
        """initializes all required modules without starting any of them."""
        self.matrix_serial = MatrixSerial(arduino_interface, matrix_width * matrix_height, arduino_baud, enable_arduino_connection)
        self.broadcast_receiver = BroadcastReceiver(discovery_port, data_port, server_name, matrix_height=matrix_height, matrix_width=matrix_width)
        self.server = Server(self.script_load_request_handler, self.script_data_handler, (matrix_width, matrix_height), data_port)
        self.canvas = Canvas(matrix_width, matrix_height)
        self.script_handler = ScriptHandler(self.canvas, self.on_draw_cycle_finished, self.server.send_object, self.server.send_object_all)

        CustomAtExit().register(self.stop)

        logging.info("manager init complete")