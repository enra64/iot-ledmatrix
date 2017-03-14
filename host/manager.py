from broadcast_receiver import BroadcastReceiver
from matgraphics import Canvas
from matserial import MatrixSerial
from script_handler import ScriptHandler
from server import Server


class Manager:
    def script_load_request_handler(self, script_name: str):
        self.script_handler.start_script(script_name)

    def script_data_handler(self, script_data):
        self.script_handler.on_data(script_data)

    def start(self):
        """starts all required modules"""
        self.matrix_serial.connect()
        self.broadcast_receiver.start()
        self.server.start()

    def stop(self):
        "gracefully stop all modules"
        self.matrix_serial.stop()
        self.broadcast_receiver.stop()
        self.server.stop()
        self.script_handler.stop_current_script()

    def __init__(self, arduino_interface, arduino_baud, matrix_width, matrix_height, discovery_port, data_port, server_name):
        """initializes all required modules without starting any of them"""
        self.matrix_serial = MatrixSerial(arduino_interface, matrix_width * matrix_height, arduino_baud)
        self.broadcast_receiver = BroadcastReceiver(discovery_port, data_port, server_name)
        self.server = Server(self.script_load_request_handler, self.script_data_handler, data_port)
        canvas = Canvas(matrix_width, matrix_height)
        self.script_handler = ScriptHandler(canvas)