import json
import threading
import logging
import zmq


class Server:
    """
    The Server class handles all client communication after discovery has been completed.
    """
    def __init__(
            self,
            script_load_request_handler,
            script_data_handler,
            on_client_connected,
            on_client_disconnected,
            matrix_dimensions = (156, 1),
            local_data_port: int = 54122):
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
        self.on_client_connected = on_client_connected
        self.on_client_disconnected = on_client_disconnected

        # stop flag
        self.receiver_thread = None
        self.abort = threading.Event()

        # storage of approved clients
        self.approved_clients = []

        # zmq socket creation
        context = zmq.Context.instance()
        self.socket = context.socket(zmq.ROUTER)

        # wait max 10ms before shutting down
        self.socket.setsockopt(zmq.LINGER, 10)

        self.logger = logging.getLogger("server")

    def handle_script_load_request(self, data, source_id):
        """
        Handle a script load request by a client.
        
        :param data: the data that was received by the client 
        :param source_id: id of the client that requested the script load 
        :return: nothing
        """
        requested_script = data['requested_script']
        self.logger.debug("received request to load " + requested_script)
        self.script_load_request_handler(requested_script, source_id)

    def handle_script_data(self, data, source_id):
        """
        Forward data received by a custom script fragment
        
        :param data: the data that was sent
        :param source_id: id of the client that sent the data
        :return: nothing
        """
        script_data = data['script_data']
        self.script_data_handler(script_data, source_id)

    def __send_json_str(self, object_as_json_str, target_id):
        """this function is the only one that should actually use the socket to send anything."""
        self.socket.send_multipart([target_id, object_as_json_str.encode("utf-8")])

    def get_client_list(self):
        """
        Get a list of currently connected and approved client ids
        
        :return: list of client ids. see pyzmq documentation. 
        """
        return self.approved_clients

    def send_object(self, obj, target_id):
        """
        Send an object to the target id. The object can be anything. No JSON serialization needs to be
        performed by you.
        
        :param obj: the object to be sent
        :param target_id: target id of the client
        :return: nothing
        """
        self.__send_json_str(json.dumps(obj), target_id)

    def send_object_all(self, obj):
        """
        Send an object to all connected clients. The object can be anything. No JSON serialization needs to be
        performed by you.

        :param obj: the object to be sent
        :return: nothing
        """
        for client_id in self.approved_clients:
            self.send_object(obj, client_id)

    def handle_connection_test(self, data, source_host):
        """
        Handles a connection test simply by replying with an appropriate message type
        
        :param data: not used
        :param source_host: the client that requested the connection check
        :return: nothing
        """
        answer = {'message_type': 'connection_test_response'}
        self.send_object(answer, source_host)

    def set_connection_request_handler(self, handler):
        """
        Set a connection request handler other than accepting all connection requests. The handler
        will get the data received by the new client, and must return either true or false
        
        :param handler: the handler to accept/deny incoming connections 
        :return: nothing
        """
        self.connection_request_handler = handler

    def handle_connection_request(self, data, source_id):
        """
        Handles connection requests by either accepting all requests, or asking the custom connection
        request handler that was set.
        
        :param data: data received in the connection request 
        :param source_id: id of the client that requested connection
        :return: nothing
        """
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
            self.on_client_connected(source_id)
            self.logger.info(str(source_id) + " has connected")
        else:
            self.send_object({'message_type': 'connection_request_response', 'granted': False}, source_id)

    def on_client_shutdown(self, data, client_id):
        """Called when a client disconnects"""
        self.approved_clients.remove(client_id)
        self.on_client_disconnected(client_id)
        self.logger.debug(str(client_id) + " has disconnected")

    def __wait(self):
        """Wait continuously for discovery requests"""

        # until stop is called
        while not self.abort.is_set():
            # wait for incoming request
            client_id, message = self.socket.recv_multipart()

            msg_decoded_json = json.loads(message.decode())
            message_type = msg_decoded_json['message_type']

            # special handling for connection requests, because those are accepted by non-approved clients
            if message_type == "connection_request":
                self.handle_connection_request(msg_decoded_json, client_id)
            # messages by approved clients will be handled now
            elif client_id in self.approved_clients:
                {
                    'connection_request': self.handle_connection_request,
                    'script_load_request': self.handle_script_load_request,
                    'script_data': self.handle_script_data,
                    'connection_test': self.handle_connection_test,
                    'shutdown_notification': self.on_client_shutdown
                }.get(message_type)(msg_decoded_json, client_id)

    def start(self):
        """Start listening for messages"""
        self.socket.bind("tcp://*:" + str(self.local_data_port))
        self.receiver_thread = threading.Thread(target=self.__wait, name="zero_server")
        self.receiver_thread.start()

    def stop(self):
        """stop the receiver thread, close receiving socket after 10ms."""
        # notify clients
        object = {"message_type": "shutdown_notification"}
        self.send_object_all(object)

        # stop receiver thread
        self.socket.close()
        self.abort.set()

    def join(self):
        """Join the thread running the receiving side of the server"""
        self.receiver_thread.join()