import json
import threading

import zmq


class Server:
    def __init__(self, script_load_request_handler, script_data_handler, local_data_port: int = 54122):
        # local data port
        self.local_data_port = local_data_port

        # handlers
        self.script_load_request_handler = script_load_request_handler
        self.script_data_handler = script_data_handler
        self.connection_request_handler = None

        # stop flag
        self.abort = threading.Event()

        # storage of approved clients
        self.approved_clients = []

        # zmq socket creation
        context = zmq.Context.instance()
        self.socket = context.socket(zmq.ROUTER)

    def handle_script_load_request(self, data, source_id):
        requested_script = data['requested_script']
        self.script_load_request_handler(requested_script, source_id)

    def handle_script_data(self, data, source_id):
        script_data = data['script_data']
        self.script_data_handler(script_data, source_id)

    def __send_json_str(self, object_as_json_str, target_id):
        """this function is the only one that should actually use the socket to send anything."""
        self.socket.send_multipart([target_id, object_as_json_str.encode("utf-8")])

    def __send_object(self, object, target_id):
        self.__send_json_str(json.dumps(object), target_id)

    def handle_connection_test(self, data, source_host):
        answer = {'message_type': 'connection_test_response'}
        self.__send_object(answer, source_host)

    def set_connection_request_handler(self, handler):
        self.connection_request_handler = handler

    def handle_connection_request(self, data, source_id):
        # accept if connection request handler does or none is set

        if self.connection_request_handler is None or self.connection_request_handler(data):
            # any accepted client has its target tuple stored
            self.approved_clients.append(source_id)
            self.__send_object({'message_type': 'connection_request_response', 'granted': True}, source_id)
        else:
            self.__send_object({'message_type': 'connection_request_response', 'granted': False}, source_id)

    def handle_print_test(self, data, source_id):
        print(str(data))
        self.__send_object({"message_type": "print_test_response", "alive": True}, source_id)

    def __wait(self):
        """Wait continuously for discovery requests"""

        # until stop is called
        while not self.abort.is_set():
            # wait for incoming request
            id, message = self.socket.recv_multipart()

            msg_json = json.loads(message.decode())
            message_type = msg_json['message_type']

            if message_type == "connection_request":
                self.handle_connection_request(msg_json, id)
            elif id in self.approved_clients:
                {
                    'script_load_request': self.handle_script_load_request,
                    'script_data': self.handle_script_data,
                    'connection_test': self.handle_connection_test,
                    'shutdown_notification': lambda json, id: self.approved_clients.remove(id),
                    'print_test': self.handle_print_test
                }.get(message_type)(msg_json, id)


    def start(self):
        self.socket.bind("tcp://*:" + str(self.local_data_port))
        threading.Thread(target=self.__wait).start()

    def stop(self):
        """stop the receiver thread"""
        self.abort.set()
