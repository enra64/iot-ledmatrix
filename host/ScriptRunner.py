import logging
import os
import threading
import time
import traceback
from functools import partial
from importlib import import_module
from typing import Callable

from helpers import utils
from Canvas import Canvas


class ScriptRunner:
    def runner(self, canvas: Canvas, draw_cycle_finished_callback):
        self.last_exec = time.time()
        self.has_crashed = False

        while not self.abort.is_set():
            # call cycle
            try:
                self.script.update(canvas)
            except Exception:
                self.logger.warning(
                    "abort execution of " + self.script_name + ": update caused an exception: " + traceback.format_exc())
                self.has_crashed = True
                self.abort.set()

            try:
                if not self.abort.is_set():
                    self.script.draw(canvas)
            except Exception:
                self.logger.warning(
                    "abort execution of " + self.script_name + ": draw caused an exception: " + traceback.format_exc())
                self.has_crashed = True
                self.abort.set()

            try:
                if not self.abort.is_set():
                    draw_cycle_finished_callback()
            except Exception:
                self.logger.error(
                    "draw cycle finish callback threw an exception. Errors here likely prohibit any matrix drawing.\n" + traceback.format_exc())
                self.has_crashed = True
                self.abort.set()

            # wait until at least 30ms have been over since last exec OR the abort flag is set
            self.abort.wait(
                timeout=utils.clamp(self.frame_period - (time.time() - self.last_exec), 0, self.frame_period))

            # update exec timestamp
            self.last_exec = time.time()

        if self.has_crashed:
            if self.script_runner_crashed_callback(self.script_name):
                self.script.restart_self()
                self.logger.info("restarting {} after crash".format(self.script_name))
            else:
                self.logger.info(
                    "not restarting {}: max tries reached or keepalive option off".format(self.script_name))
        try:
            if self.ok:
                self.script.exit()
        except Exception:
            self.logger.warning(self.script_name + ": exit caused an exception:\n" + traceback.format_exc())

    def start(self):
        self.script_thread.start()

    def stop(self):
        self.abort.set()
        self.join()

    def on_data(self, data, source_id):
        if not self.ok:
            return
        try:
            self.script.on_data(data, source_id)
        except Exception:
            self.logger.warning(self.script_name + ": on_data caused an exception:\n" + traceback.format_exc())

    def on_client_connected(self, client_id):
        """forward client connect signal"""
        if not self.ok:
            return
        try:
            self.script.on_client_connected(client_id)
        except Exception:
            self.logger.warning(
                self.script_name + ": on_client_connected caused an exception:\n" + traceback.format_exc())

    def on_client_disconnected(self, client_id):
        """forward client disconnect signal"""
        if not self.ok:
            return
        try:
            self.script.on_client_disconnected(client_id)
        except Exception:
            self.logger.warning(
                self.script_name + ": on_client_disconnected caused an exception:\n" + traceback.format_exc())

    def join(self):
        try:
            if self.script_thread is not None:
                self.script_thread.join()
        # called when process was never started
        except RuntimeError:
            logging.info(self.script_name + " joined before starting")

    def set_frame_period(self, period):
        """
        Change the frame period with which the script will be updated

        :param period: the target frame period. resulting frame rate must be 0 <= f <= 60, in Hz, so the input is in sec
        :return: nothing
        """
        self.set_frame_rate(1 / period)

    def set_frame_rate(self, frame_rate):
        """
        Change the frame rate with which the script will be updated
         
        :param frame_rate: the target frame rate. must be 0 <= f <= 60, in Hz 
        :return: nothing
        """
        assert 0 <= frame_rate <= 60, "Frame rate out of bounds."
        self.frame_period = 1 / frame_rate

    def __init__(self,
                 script: str,
                 canvas: Canvas,
                 draw_cycle_finished_callback: Callable,
                 send_object: Callable,
                 send_object_to_all: Callable,
                 start_script: Callable,
                 get_connected_clients: Callable,
                 script_runner_crashed: Callable[[str], bool]):
        # get me some logger
        self.logger = logging.getLogger("scriptrunner")

        # default to 30ms frame period
        self.default_frame_period = 0.030
        self.frame_period = self.default_frame_period

        # default to bad init
        self.ok = False
        self.script_thread = None

        # store script name for debugging
        self.script_name = script

        # abort flag for stopping the run thread
        self.abort = threading.Event()

        # last exec time init so pycharm doesnt whine
        self.last_exec = 0

        # initialize the dont-crash-too-often logic
        self.script_runner_crashed_callback = script_runner_crashed

        # dynamic import
        try:
            # allow importing scripts what are in their own folder
            if os.path.isdir("scripts/" + script):
                script_path = "scripts/{0}/{0}.py".format(script)
            else:
                script_path = "scripts/{}.py".format(script)

            if os.path.isfile(script_path):
                script_module_path = script_path.replace("/", ".").replace(".py", "")
                script_module = import_module(script_module_path)
            else:
                self.logger.error(script + " not found, aborting")
                return
        except SyntaxError:
            self.logger.warning("parsing " + script + " produced a SyntaxError\n" + traceback.format_exc())
        else:  # if import produced no syntax error
            self.logger.debug(f"Successfully imported {script}")
            try:
                # "restart self" helper
                restart_script_function = partial(start_script, script_name=script, source_id="self restart")
                # call custom script constructor
                self.script = getattr(script_module, script)(
                    canvas,
                    send_object,
                    send_object_to_all,
                    start_script,
                    restart_script_function,
                    self.set_frame_period,
                    self.set_frame_rate,
                    get_connected_clients
                )
            except AttributeError:
                self.logger.error(
                    "{} has no class or attribute called {}. "
                    "The script class must have the exact same name as the script file "
                    "and, if applicable, the script directory.".format(script_path, script))
                traceback.print_exc()

            except Exception:
                self.logger.warning(script + ": __init__ caused an exception:\n" + traceback.format_exc())
            else:
                self.script_thread = threading.Thread(
                    target=self.runner,
                    args=(
                        canvas,
                        draw_cycle_finished_callback
                    ),
                    name="CUSTOM SCRIPT RUNNER FOR \"" + script + "\""
                )
                self.ok = True
