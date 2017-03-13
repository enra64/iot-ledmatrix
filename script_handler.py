from importlib import import_module # import all the things
import threading
import helpers
import time

from matgraphics import Canvas


class ScriptRunner:
    def runner(self, canvas: Canvas):
        self.last_exec = time.time()

        while not self.abort.is_set():
            # wait until at least 30ms have been over since last exec
            time.sleep(helpers.clamp(0.030 - (time.time() - self.last_exec), 0, 0.03))

            # update exec timestamp
            self.last_exec = time.time()

            # call cycle
            self.script.update(canvas)
            self.script.draw(canvas)

        self.script.exit()

    def start(self):
        self.process.start()

    def stop(self):
        self.abort.set()
        self.process.join()

    def __init__(self, script:str, canvas: Canvas):
        module = import_module('scripts.' + script)
        self.script = getattr(module, script)()
        self.process = threading.Thread(target=self.runner, args={canvas,})
        self.abort = threading.Event()
        self.last_exec = 0


class ScriptHandler:
    def __init__(self, canvas: Canvas):
        self.current_script_runner = None
        self.canvas = canvas
        self.currently_running_script = False

    def start_script(self, script_name: str):
        """Will load the class in the scripts/ folder that has the given name in the file with the same name.
        :param script_name: the name of _both_ the script and the class implementing the callback functions"""
        self.current_script_runner = ScriptRunner(script_name, self.canvas)
        self.__start_current_script()

    def script_running(self):
        return self.currently_running_script

    def __start_current_script(self):
        if self.currently_running_script:
            self.stop_current_script()
        self.current_script_runner.start()
        self.currently_running_script = True

    def stop_current_script(self):
        self.current_script_runner.stop()
        self.currently_running_script = False