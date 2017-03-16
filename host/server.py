from socket import *
import json
import threading


class Server:
    def __init__(self, script_load_request_handler, script_data_handler, local_data_port: int = 54122):
        self.local_data_port = local_data_port
        self.abort = threading.Event()
        self.script_load_request_handler = script_load_request_handler
        self.script_data_handler = script_data_handler
        self.connection_request_handler = None
        self.approved_clients = {}

    def handle_script_load_request(self, data, source_host):
        requested_script = data['requested_script']
        self.script_load_request_handler(requested_script, source_host)

    def handle_script_data(self, data, source_host):
        script_data = data['script_data']
        self.script_data_handler(script_data, source_host)

    def __send_json_str(self, object_as_json_str, target_host):
        """this function is the only one that should actually use the socket to send anything."""
        send_socket = socket(AF_INET, SOCK_STREAM)
        send_socket.connect(target_host)
        send_socket.send(object_as_json_str.encode("utf-8"))
        send_socket.close()

    def __send_object(self, object, receiving_host):
        self.__send_json_str(json.dumps(object), receiving_host)

    def handle_connection_test(self, data, source_host):
        answer = {'message_type': 'connection_test_response'}
        self.__send_object(answer, source_host)

    def set_connection_request_handler(self, handler):
        self.connection_request_handler = handler

    def handle_connection_request(self, data, source_host):
        # accept if connection request handler does or none is set
        client_id_tuple = (source_host[0], data['data_port'])
        if self.connection_request_handler is None or self.connection_request_handler(data):
            # any accepted client has its target tuple stored
            self.approved_clients[source_host[0]] = client_id_tuple
            self.__send_object({'message_type': 'connection_request_answer', 'granted': True}, client_id_tuple)
        else:
            self.__send_object({'message_type': 'connection_request_answer', 'granted': False}, client_id_tuple)

    def __wait(self):
        """Wait continuously for discovery requests"""
        # config and bind waiting socket
        receiving_socket = socket(AF_INET, SOCK_STREAM)
        receiving_socket.bind(('', self.local_data_port))
        receiving_socket.listen()
        receiving_socket.settimeout(.5)

#   see http://stackoverflow.com/questions/34249188/oserror-errno-107-transport-endpoint-is-not-connected
        # for correct implementation

        # until the parents stop is called
        while not self.abort.is_set():
            try:
                # wait for incoming request
                connection, source_host = receiving_socket.accept()

                received_string = connection.recv(4096).decode("utf-8")

                # decode the incoming message
                received_json = json.loads(received_string)

                message_type = received_json['message_type']

                print("got " + received_string)

                if message_type == 'connection_request':
                    self.handle_connection_request(received_json, source_host)
                elif source_host in self.approved_clients:
                    # update the host with the data port we have stored for his address
                    source_host = self.approved_clients[source_host[0]]

                    # call the handler function appropriate for the message type
                    {
                        'script_load_request': self.handle_script_load_request,
                        'script_data': self.handle_script_data,
                        'connection_test': self.handle_connection_test,
                    }.get(message_type)(received_json, source_host)
                connection.close()
            except timeout:
                pass # ignore timeout, required for listening loop

        receiving_socket.close()

    def start(self):
        """start the receiver thread"""
        threading.Thread(target=self.__wait).start()

    def stop(self):
        """stop the receiver thread"""
        self.abort.set()
