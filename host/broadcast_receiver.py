from socket import *
import json
import threading

class BroadcastReceiver:
    """This class can be started and stopped. It will respond to incoming JSON discovery messages with the address and data port of the server"""

    def __init__(self, discovery_port: int = 54123, data_port: int = 54122, name: str = "matserver"):
        """
        Init the BroadcastReceiver.

        :param discovery_port: the port on which the receiver should listen for discovery messages
        :param data_port: the port on which the server is listening for all other messages
        :param name: the name of this server
        """
        self.discovery_port = discovery_port
        self.abort = threading.Event()
        self.self_description = json.dumps({'port': data_port, 'name': name})

    def __wait(self):
        """Wait continuously for discovery requests"""
        # config and bind waiting socket
        receiver_socket = socket(AF_INET, SOCK_DGRAM)
        receiver_socket.bind(('', self.discovery_port))
        receiver_socket.settimeout(.5)

        # until the parents stop is called
        while not self.abort.is_set():
            # wait for incoming request
            received, source_address = receiver_socket.recvfrom(4096)

            # decode the incoming message
            json_recv = json.loads(received)
            if json_recv['message_type'] == "discovery":
                # answer with our own server identification
                response_port = json_recv['data_port']
                response_socket = socket(AF_INET, SOCK_DGRAM)
                response_socket.sendto(self.self_description, (source_address, response_port))

        receiver_socket.close()

    def start(self):
        """start the receiver thread"""
        threading.Thread(target=self.__wait)

    def stop(self):
        """stop the receiver thread"""
        self.abort.set()