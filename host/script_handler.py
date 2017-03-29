import traceback
from importlib import import_module # import all the things
import threading

import logging

import helpers
import time

from canvas import Canvas


class ScriptRunner:
    def runner(self, canvas: Canvas, draw_cycle_finished_callback):
        self.last_exec = time.time()

        while not self.abort.is_set():
            # wait until at least 30ms have been over since last exec
            time.sleep(helpers.clamp(0.030 - (time.time() - self.last_exec), 0, 0.03))

            # update exec timestamp
            self.last_exec = time.time()

            # call cycle
            try:
                self.script.update(canvas)
                self.script.draw(canvas)
                draw_cycle_finished_callback()
            except (AssertionError, Exception) as detail:
                logging.error(self.script_name + ": caused an exception: " + str(detail) + ", execution will be stopped.")
                self.abort.set()

        self.script.exit()

    def start(self):
        self.script_thread.start()

    def stop(self):
        self.abort.set()
        try:
            self.script_thread.join()
        # called when process was never started
        except RuntimeError:
            print(self.script_name + " stopped before starting")

    def on_data(self, data, source_id):
        try:
            self.script.on_data(data, source_id)
        except Exception as detail:
            logging.error(self.script_name + ": on_data caused an exception: " + str(detail))

    def on_new_client(self, client_id):
        self.script.on_new_client(client_id)

    def on_client_disconnected(self, client_id):
        self.script.on_client_disconnected(client_id)

    def join(self):
        self.script_thread.join()

    def __init__(self, script:str, canvas: Canvas, draw_cycle_finished_callback, send_object, send_object_to_all, start_script):
        self.ok = False
        try:
            module = import_module('scripts.' + script)
        except SyntaxError:
            logging.error("module import of " + script + " produced a syntaxerror " + traceback.format_exc())
        else:
            try:
                self.script = getattr(module, script)(canvas, send_object, send_object_to_all, start_script)
            except Exception as detail:
                logging.error(script + ": __init__ caused an exception: " + str(detail))
            else:
                self.script_thread = threading.Thread(target=self.runner, args=(canvas, draw_cycle_finished_callback), name="script thread: " + script)
                self.abort = threading.Event()
                self.last_exec = 0
                self.script_name = script
                self.ok = True


class ScriptHandler:
    def __init__(self, canvas: Canvas, draw_cycle_finish_callback, send_object, send_object_to_all):
        self.current_script_runner = None
        self.canvas = canvas
        self.is_script_running = False
        self.draw_cycle_finished_callback = draw_cycle_finish_callback
        self.send_object = send_object
        self.send_object_to_all = send_object_to_all

    def start_script(self, script_name: str, source_id):
        """Will load the class in the scripts/ folder that has the given name in the file with the same name.
        :param script_name: the name of _both_ the script and the class implementing the callback functions"""
        if self.is_script_running:
            self.stop_current_script()

        self.current_script_runner = ScriptRunner(script_name, self.canvas, self.draw_cycle_finished_callback, self.send_object, self.send_object_to_all, self.start_script)
        if self.current_script_runner.ok:
            logging.info("START: " + script_name)
            self.current_script_runner.start()
            self.is_script_running = True
        else:
            logging.warning("script '" + script_name + "' not executed due to initialization failure. check your code!")

    def script_running(self):
        return self.is_script_running

    def on_data(self, data, source_id):
        self.current_script_runner.on_data(data, source_id)

    def stop_current_script(self):
        logging.info("STOP: " + self.current_script_runner.script_name)
        self.current_script_runner.stop()
        self.is_script_running = False

    def join(self):
        self.current_script_runner.join()