import time
import random

from matgraphics import Canvas

class echo_test:
    def __init__(self, canvas, send_object, send_object_to_all):
        self.send_object = send_object

    def update(self, canvas):
        pass

    def draw(self, canvas: Canvas):
        pass

    def on_data(self, json, source_id):
        self.send_object({"message_type": "print_test_response", "received": json}, source_id)

    def exit(self):
        pass