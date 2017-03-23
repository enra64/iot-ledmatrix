import json
import threading
import logging
import zmq


class Server:

    def __init__(self, script_load_request_handler, script_data_handler, matrix_dimensions = (156, 1), local_data_port: int = 54122):
        self.logger = logging.getLogger("ledmatrix.server")

        # local data port
        self.local_data_port = local_data_port

        # store matrix dimensions
        self.matrix_width = matrix_dimensions[0]
        self.matrix_height = matrix_dimensions[1]

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
        logging.debug("server received request to load " + requested_script)
        self.script_load_request_handler(requested_script, source_id)

    def handle_script_data(self, data, source_id):
        script_data = data['script_data']
        self.script_data_handler(script_data, source_id)

    def __send_json_str(self, object_as_json_str, target_id):
        """this function is the only one that should actually use the socket to send anything."""
        self.socket.send_multipart([target_id, object_as_json_str.encode("utf-8")])

    def send_object(self, object, target_id):
        self.__send_json_str(json.dumps(object), target_id)

    def send_object_all(self, object):
        for id in self.approved_clients:
            self.send_object(object, id)

    def handle_connection_test(self, data, source_host):
        answer = {'message_type': 'connection_test_response'}
        self.send_object(answer, source_host)

    def set_connection_request_handler(self, handler):
        self.connection_request_handler = handler

    def handle_connection_request(self, data, source_id):
        # accept if connection request handler does or none is set

        if self.connection_request_handler is None or self.connection_request_handler(data):
            # any accepted client has its target tuple stored
            self.approved_clients.append(source_id)
            response_object = {
                'message_type': 'connection_request_response',
                'granted': True,
                'matrix_width': self.matrix_width,
                'matrix_height': self.matrix_height}
            self.send_object(response_object, source_id)
            logging.info("id: " + str(source_id) + " has connected")
        else:
            self.send_object({'message_type': 'connection_request_response', 'granted': False}, source_id)

    def on_client_shutdown(self, data, client_id):
        self.approved_clients.remove(client_id),
        logging.debug(str(client_id) + " has disconnected")

    def __wait(self):
        """Wait continuously for discovery requests"""

        # until stop is called
        while not self.abort.is_set():
            # wait for incoming request
            id, message = self.socket.recv_multipart()

            msg_decoded_json = json.loads(message.decode())
            message_type = msg_decoded_json['message_type']

            if message_type == "connection_request":
                self.handle_connection_request(msg_decoded_json, id)
            elif id in self.approved_clients:
                {
                    'script_load_request': self.handle_script_load_request,
                    'script_data': self.handle_script_data,
                    'connection_test': self.handle_connection_test,
                    'shutdown_notification': self.on_client_shutdown
                }.get(message_type)(msg_decoded_json, id)

        self.socket.close()

    def start(self):
        self.socket.bind("tcp://*:" + str(self.local_data_port))
        self.receiver_thread = threading.Thread(target=self.__wait, name="zero_server")
        self.receiver_thread.start()

    def stop(self):
        """stop the receiver thread"""
        # notify clients
        object = {"message_type": "shutdown_notification"}
        self.send_object_all(object)

        # wait max 10ms before shutting down
        self.socket.setsockopt(zmq.LINGER, 10)
        self.socket.close()

        # stop receiver thread
        self.abort.set()

    def join(self):
        self.receiver_thread.join()