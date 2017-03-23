from matgraphics import Canvas


class log_reader:
    def __init__(self, canvas, send_object, send_object_to_all, start_script):
        self.send_object = send_object
        self.start_script = start_script

    def update(self, canvas):
        pass

    def draw(self, canvas: Canvas):
        pass

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

    def exit(self):
        pass