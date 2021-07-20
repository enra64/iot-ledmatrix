import sys
from time import sleep

import zmq


def server(port: str):
    # zmq socket creation
    context = zmq.Context.instance()
    # noinspection PyUnresolvedReferences
    socket = context.socket(zmq.ROUTER)
    # noinspection PyUnresolvedReferences
    socket.setsockopt(zmq.IPV6, True)
    # wait max 10ms before shutting down
    # noinspection PyUnresolvedReferences
    socket.setsockopt(zmq.LINGER, 10)

    socket.bind("tcp://*:" + str(port))
    # wait for incoming request
    while True:
        test = socket.recv_multipart()
        print(f"Received message: {test}")



def request_connection(address: str, port: str):
    if ":" in address:
        address = f"[{address}]"
    # zmq socket creation
    context = zmq.Context.instance()
    # noinspection PyUnresolvedReferences
    socket = context.socket(zmq.DEALER)
    # noinspection PyUnresolvedReferences
    socket.setsockopt(zmq.IPV6, True)
    # wait max 10ms before shutting down
    # noinspection PyUnresolvedReferences
    socket.setsockopt(zmq.LINGER, 10)


    connection_string = f"tcp://{address}:{port}"
    print(f"Connecting to {connection_string}")
    context_manager = socket.connect(connection_string)
    print(f"Connect_ok is {context_manager}")
    sleep(1)

    while True:
        sent = socket.send_string("test")
        print(f"sent is {sent}")
        sleep(1)


if __name__ == "__main__":
    if sys.argv[1] == "server":
        server(*sys.argv[3:])
    else:
        request_connection(*sys.argv[2:])
