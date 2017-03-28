from CustomScript import CustomScript
from matgraphics import Canvas


class log_reader(CustomScript):
    def __init__(self, canvas, send_object, send_object_to_all, start_script):
        super().__init__(canvas, send_object, send_object_to_all, start_script)

    def on_data(self, json, source_id):
        command = json['command']

        if command == "give_me_log_pls":
            log = []
            with open("ledmatrix.log") as f:
                # reverse file (inplace)
                reversed = f.readlines()
                reversed.reverse()

                for line in reversed:
                    log.append(line)
            self.send_object({"message_type": "bogus", "log": log}, source_id)
