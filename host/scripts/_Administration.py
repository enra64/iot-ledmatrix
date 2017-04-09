import logging
import os
import sys

from CustomScript import CustomScript
from helpers.custom_atexit import CustomAtExit


class _Administration(CustomScript):
    def __init__(self, canvas, send_object, send_object_to_all, start_script, restart_self, set_frame_period,
                 set_frame_rate, get_connected_clients):
        super().__init__(canvas, send_object, send_object_to_all, start_script, restart_self, set_frame_period,
                         set_frame_rate, get_connected_clients)

    def on_data(self, json, source_id):
        command = json['command']
        if command == "echo_test":
            self.send_object({"message_type": "print_test_response", "received": json}, source_id)
        elif command == "reboot_rpi":
            logging.info("rebooting pi on command")
            CustomAtExit().trigger()
            os.system('/sbin/sudo /sbin/reboot now')
        elif command == "shutdown_rpi":
            logging.info("shutting down pi on command")
            CustomAtExit().trigger()
            os.system('sudo shutdown now')
        elif command == "restart_matrix_server":
            logging.info("restarting server script. somewhat finicky...")
            CustomAtExit().trigger()
            python = sys.executable
            os.execl(python, python, *sys.argv)
        else:
            self.send_object({"message_type": "unrecognized_command_warning"}, source_id)
