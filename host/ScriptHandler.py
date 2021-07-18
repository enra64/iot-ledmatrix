import logging

from Canvas import Canvas
from ScriptRunner import ScriptRunner
from helpers.custom_atexit import CustomAtExit


class ScriptHandler:
    def __init__(
            self,
            canvas: Canvas,
            draw_cycle_finish_callback,
            send_object,
            send_object_to_all,
            get_client_list,
            keepalive):
        """
        
        :param canvas: canvas that will be drawn to. can be accessed for the back buffer required to get data to leds 
        :param draw_cycle_finish_callback: method to be called whenever the draw cycle of the current script has finished
        :param send_object: method to send an object to a single client
        :param send_object_to_all: method to send an object to all clients
        :param get_client_list: method that returns list of zmq (Server) client ids
        :param keepalive: setting True here will restart scripts that have crashed
        """
        self.current_script_runner = None
        self.canvas = canvas
        self.is_script_running = False
        self.draw_cycle_finished_callback = draw_cycle_finish_callback
        self.send_object = send_object
        self.send_object_to_all = send_object_to_all
        self.get_client_list = get_client_list
        self.keepalive = keepalive
        self.logger = logging.getLogger("scripthandler")
        self.crash_counter = {}

    def restart_current_script(self):
        self.current_script_runner.restart_script()

    def start_script(self, script_name: str, source_id):
        """
        Will load the class in the scripts/ folder that has the given name in the file with the same name.
        
        :param source_id: reason for why this script is being started
        :param script_name: the name of _both_ the script and the class implementing the callback functions
        """
        if self.is_script_running:
            self.stop_current_script()
        self.is_script_running = False

        self.current_script_runner = \
            ScriptRunner(
                script_name,
                self.canvas,
                self.draw_cycle_finished_callback,
                self.send_object,
                self.send_object_to_all,
                self.start_script,
                self.get_client_list,
                self.script_runner_crashed
            )

        # don't start the new script if CustomAtExit was triggered
        if self.current_script_runner.ok and not CustomAtExit().is_shutdown_initiated():
            # no warning to user necessary here, as the script handler already logs a lot of information
            self.logger.info(f"START OK: {script_name}")
            self.current_script_runner.start()
            self.is_script_running = True
        elif not CustomAtExit().is_shutdown_initiated():
            self.logger.warning(f"START FAILED: {script_name}")
        else:
            self.logger.warning(f"Not starting {script_name} - shutdown was initiated")

    def script_runner_crashed(self, script_name: str) -> bool:
        if not self.keepalive:
            return False

        if script_name in self.crash_counter:
            self.crash_counter[script_name] += 1
        else:
            self.crash_counter[script_name] = 1

        return self.crash_counter[script_name] < 10

    def script_running(self):
        return self.is_script_running

    def on_client_connected(self, id):
        if self.current_script_runner is not None:
            self.current_script_runner.on_client_connected(id)

    def on_client_disconnected(self, id):
        if self.current_script_runner is not None:
            self.current_script_runner.on_client_disconnected(id)

    def on_data(self, data, source_id):
        if self.current_script_runner is not None:
            self.current_script_runner.on_data(data, source_id)

    def stop_current_script(self):
        if self.current_script_runner is None:
            self.logger.info("STOP: NO RUNNING SCRIPT")
        else:
            self.logger.info("STOP: " + self.current_script_runner.script_name)
            self.current_script_runner.stop()
        self.is_script_running = False

    def join(self):
        if self.current_script_runner is not None:
            self.current_script_runner.join()
