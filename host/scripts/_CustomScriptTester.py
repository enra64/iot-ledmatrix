import time

import Canvas
from CustomScript import CustomScript


class _CustomScriptTester(CustomScript):
    def __init__(self, canvas, send_object, send_object_to_all, start_script, restart_self, set_frame_period,
                 set_frame_rate, get_connected_clients):
        super().__init__(canvas, send_object, send_object_to_all, start_script, restart_self, set_frame_period,
                         set_frame_rate, get_connected_clients)

        print("initializing _CustomScriptTester")

        self.last_update_call = time.time()

        print("requesting update period of .04s")
        set_frame_period(0.04)

        print("printing currently connected clients:")
        print(*self.get_connected_clients())

        print("untested methods are: start_script, send_object(_to_all)")

    def on_client_disconnected(self, id):
        print(id + " dc'ed")

    def on_data(self, data_dictionary, source_id):
        print("got " + data_dictionary + " from " + source_id)

    def restart_self(self):
        print("script should be restarting right about now")

    def update(self, canvas):
        print("received update call after " + str(time.time() - self.last_update_call) + "s")
        self.last_update_call = time.time()

    def exit(self):
        print("_CustomScriptTester exiting")

    def draw(self, canvas: Canvas):
        print("draw call")

    def on_client_connected(self, id):
        print(id + " connected")
