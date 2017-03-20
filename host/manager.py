import logging

from broadcast_receiver import BroadcastReceiver
from custom_atexit import CustomAtExit
from matgraphics import Canvas
from matserial import MatrixSerial
from script_handler import ScriptHandler
from zero_server import Server


class Manager:
    def script_load_request_handler(self, script_name: str, source_id):
        self.script_handler.start_script(script_name, source_id)

    def script_data_handler(self, script_data, source_id):
        self.script_handler.on_data(script_data, source_id)

    def on_draw_cycle_finished(self):
        self.matrix_serial.update(self.canvas.get_buffer())

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
        self.script_handler.start_script(script, "hardcoded")

    def on_shutdown(self):
        self.stop()

    def __init__(self, arduino_interface, arduino_baud, matrix_width, matrix_height, data_port, server_name, discovery_port):
        """initializes all required modules without starting any of them. DiscoveryPort hardcoded to 54123"""
        self.matrix_serial = MatrixSerial(arduino_interface, matrix_width * matrix_height, arduino_baud)
        self.broadcast_receiver = BroadcastReceiver(discovery_port, data_port, server_name)
        self.server = Server(self.script_load_request_handler, self.script_data_handler, (matrix_width, matrix_height), data_port)
        self.canvas = Canvas(matrix_width, matrix_height)
        self.script_handler = ScriptHandler(self.canvas, self.on_draw_cycle_finished, self.server.send_object, self.server.send_object_all)

        CustomAtExit().register(self.stop)

        logging.info("manager init complete")