import logging
from typing import Optional

import pytz

import Canvas
from CustomScript import CustomScript
from datetime import datetime, timedelta
import RPi.GPIO as GPIO

from helpers.Color import Color


class _WakeUpLight(CustomScript):
    def __init__(self, canvas, send_object, send_object_to_all, start_script, restart_self, set_frame_period,
                 set_frame_rate, get_connected_clients):
        super().__init__(canvas, send_object, send_object_to_all, start_script, restart_self, set_frame_period,
                         set_frame_rate, get_connected_clients)
        # setup
        self.logger = logging.getLogger("script:wakeuplight")
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        self.set_frame_rate(24)
        self._last_force_switch_status = self._read_force_switch()
        self._light_percentage = 0
        self.logger.info("Started")

    def _read_force_switch(self) -> bool:
        return GPIO.input(17) == GPIO.LOW

    def update(self, canvas):
        force_switch = self._read_force_switch()
        if force_switch != self._last_force_switch_status:
            self._light_percentage = -0.2
            self._last_force_switch_status = force_switch

        if self._light_percentage < 0:
            light_percentage = 0
        elif self._light_percentage > 1:
            light_percentage = 1
        else:
            light_percentage = self._light_percentage

        color_temp = 1400 + (5500 - 1400) * light_percentage
        color_value = Color.from_temperature(color_temp, light_percentage)
        self.current_color = color_value

        self._light_percentage += 0.005

        if self._light_percentage > 1.5:
            self._light_percentage = -0.2


    def draw(self, canvas: Canvas):
        canvas.clear(self.current_color)

    def on_data(self, json, source_id):
        pass
