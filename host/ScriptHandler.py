import logging

from Canvas import Canvas
from ScriptRunner import ScriptRunner


class ScriptHandler:
    def __init__(
            self,
            canvas: Canvas,
            draw_cycle_finish_callback,
            send_object,
            send_object_to_all,
            get_client_list):
        """
        
        :param canvas: canvas that will be drawn to. can be accessed for the back buffer required to get data to leds 
        :param draw_cycle_finish_callback: method to be called whenever the draw cycle of the current script has finished
        :param send_object: method to send an object to a single client
        :param send_object_to_all: method to send an object to all clients
        :param get_client_list: method that returns list of zmq (Server) client ids
        """
        self.current_script_runner = None
        self.canvas = canvas
        self.is_script_running = False
        self.draw_cycle_finished_callback = draw_cycle_finish_callback
        self.send_object = send_object
        self.send_object_to_all = send_object_to_all
        self.get_client_list = get_client_list
        self.logger = logging.getLogger("scripthandler")

    def start_script(self, script_name: str, source_id):
        """
        Will load the class in the scripts/ folder that has the given name in the file with the same name.
        
        :param script_name: the name of _both_ the script and the class implementing the callback functions
        """
        if self.is_script_running:
            self.stop_current_script()

        self.current_script_runner = \
            ScriptRunner(
                script_name,
                self.canvas,
                self.draw_cycle_finished_callback,
                self.send_object,
                self.send_object_to_all,
                self.start_script,
                self.get_client_list)

        if self.current_script_runner.ok:
            # no warning to user necessary here, as the script handler already logs a lot of information
            self.logger.info("START: " + script_name)
            self.current_script_runner.start()
            self.is_script_running = True

    def script_running(self):
        return self.is_script_running

    def on_client_connected(self, id):
        self.current_script_runner.on_client_connected(id)

    def on_client_disconnected(self, id):
        self.current_script_runner.on_client_disconnected(id)

    def on_data(self, data, source_id):
        self.current_script_runner.on_data(data, source_id)

    def stop_current_script(self):
        if self.current_script_runner is None:
            self.logger.info("STOP: NO RUNNING SCRIPT")
        else:
            self.logger.info("STOP: " + self.current_script_runner.script_name)
            self.current_script_runner.stop()
        self.is_script_running = False

    def join(self):
        self.current_script_runner.join()
