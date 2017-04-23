from os import listdir
from os.path import isfile, join

import logging

from CustomScript import CustomScript


class _ScriptLoader(CustomScript):
    def __init__(self, canvas, send_object, send_object_to_all, start_script, restart_self, set_frame_period,
                 set_frame_rate, get_connected_clients):
        super().__init__(canvas, send_object, send_object_to_all, start_script, restart_self, set_frame_period,
                         set_frame_rate, get_connected_clients)

    def on_data(self, json, source_id):
        command = json['command']

        if command == "request_script_list":
            scripts = [f[:-3] for f in listdir("scripts/") if isfile(join("scripts/", f)) and not f.startswith("_")]
            self.send_object({"message_type": "request_script_list", "script_list": scripts}, source_id)
        elif command == "script_load_request":
            requested_script = json['requested_script']
            logging.info("user requested script " + requested_script)
            self.start_script(requested_script, source_id)
