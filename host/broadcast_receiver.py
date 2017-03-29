from socket import *
import json
import threading


class BroadcastReceiver:
    """
    The BroadcastReceiver answers to all client discovery requests with a description of this server.
    All communication is in JSON. 
    """

    def __init__(
            self,
            discovery_port: int = 54123,
            data_port: int = 54122,
            name: str = "matserver",
            matrix_width: int = 0,
            matrix_height: int = 0):
        """
        Init the BroadcastReceiver.

        :param discovery_port: the port on which the receiver should listen for discovery messages
        :param data_port: the port on which the server is listening for all other messages
        :param name: the name of this server
        :param matrix_height: number of vertical pixels in the matrix, for display in the client
        :param matrix_width: number of horizontal pixels in the matrix, for display in the client
        """
        self.discovery_port = discovery_port
        self.data_port = data_port
        self.abort = threading.Event()
        # create a self description in the json format expected by the clients
        self.self_description = json.dumps(
            {
                'data_port': data_port,
                'name': name,
                'matrix_width': matrix_width,
                'matrix_height': matrix_height
            })

    def __wait(self):
        """Wait continuously for discovery requests"""
        # config and bind waiting socket
        receiver_socket = socket(AF_INET, SOCK_DGRAM)
        receiver_socket.bind(('', self.discovery_port))
        receiver_socket.settimeout(.5)

        # until the parents stop is called
        while not self.abort.is_set():
            # wait for incoming request
            try:
                received, source_address = receiver_socket.recvfrom(4096)

                # decode the incoming message
                json_recv = json.loads(received.decode("utf-8"))
                if json_recv['message_type'] == "discovery":
                    # answer with our own server identification
                    response_port = json_recv['discovery_port']
                    response_socket = socket(AF_INET, SOCK_DGRAM)
                    response_socket.sendto(self.self_description.encode('utf-8'), (source_address[0], response_port))

            # we want to continue looping after each timeout (except if abort flag is set)
            except timeout:
                continue

        receiver_socket.close()

    def join(self):
        """
        Calls join() on the internal thread. Used to wait for exit on all threads.
        """
        self.receiver_thread.join()

    def start(self):
        """Start the BroadcastReceiver."""
        self.receiver_thread = threading.Thread(target=self.__wait, name="broadcast receiver")
        self.receiver_thread.start()

    def stop(self):
        """Stop the BroadcastReceiver"""
        self.abort.set()

    def get_advertised_data_port(self):
        """
        Get the advertised data port, that is, the port that new clients will be told we are listening at.
        
        :return: the port number
        """
        return self.data_port
