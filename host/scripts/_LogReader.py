import logging

from CustomScript import CustomScript


class _LogReader(CustomScript):
    def __init__(self, canvas, send_object, send_object_to_all, start_script, restart_self, set_frame_period,
                 set_frame_rate, get_connected_clients):
        super().__init__(canvas, send_object, send_object_to_all, start_script, restart_self, set_frame_period,
                         set_frame_rate, get_connected_clients)

    def on_data(self, json, source_id):
        command = json['command']

        if command == "give_me_log_pls":
            log = []
            try:
                logfilename = "ledmatrix.log"

                logging_handlers = logging._handlerList
                for handler in logging_handlers:
                    if isinstance(handler(), logging.FileHandler):
                        logfilename = handler().baseFilename

                with open(logfilename) as f:
                    # reverse file (inplace)
                    reversed = f.readlines()
                    reversed.reverse()

                    for line in reversed:
                        log.append(line)
                self.send_object({"message_type": "bogus", "log": log}, source_id)
            except FileNotFoundError:
                self.send_object({"message_type": "bogus", "log": "No log file found, tried '{}'".format(logfilename)}, source_id)