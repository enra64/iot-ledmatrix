from socket import *
import json
import threading

class Server:
    def __init__(self, script_load_request_handler, script_data_handler, data_port: int = 54122):
        self.data_port = data_port
        self.abort = threading.Event()
        self.script_load_request_handler = script_load_request_handler
        self.script_data_handler = script_data_handler

    def handle_script_load_request(self, data):
        requested_script = data['requested_script']
        self.script_load_request_handler(requested_script)

    def handle_script_data(self, data):
        script_data = data['script_data']
        self.script_data_handler(script_data)

    def __wait(self):
        """Wait continuously for discovery requests"""
        # config and bind waiting socket
        receiver_socket = socket(AF_INET, SOCK_STREAM)
        receiver_socket.bind(('', self.data_port))
        receiver_socket.settimeout(.5)

        # until the parents stop is called
        while not self.abort.is_set():
            # wait for incoming request
            received, source_address = receiver_socket.recvfrom(4096)

            # decode the incoming message
            received_json = json.loads(received)

            # call the handler function appropriate for the message type
            {
                'script_load_request': self.handle_script_load_request,
                'script_data': self.handle_script_data
            }.get(received_json['message_type'])(received_json)

        receiver_socket.close()

    def start(self):
        """start the receiver thread"""
        threading.Thread(target=self.__wait)

    def stop(self):
        """stop the receiver thread"""
        self.abort.set()