import os

import sys

from matgraphics import Canvas

class administration:
    def __init__(self, canvas, send_object, send_object_to_all):
        self.send_object = send_object

    def update(self, canvas):
        pass

    def draw(self, canvas: Canvas):
        pass

    def on_data(self, json, source_id):
        command = json['command']
        if command == "echo_test":
            self.send_object({"message_type": "print_test_response", "received": json}, source_id)
        elif command == "reboot_rpi":
            os.system('reboot')
        elif command == "restart_matrix_server":
            os.execv(sys.executable, ['python'] + sys.argv)
        else:
            self.send_object({"message_type": "unrecognized_command_warning"}, source_id)

    def exit(self):
        pass