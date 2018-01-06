import logging
import pytz
from pyparsing import col

import Canvas
from CustomScript import CustomScript
from datetime import datetime, timedelta

from helpers.Color import Color


class _WakeUpLight(CustomScript):
    def __init__(self, canvas, send_object, send_object_to_all, start_script, restart_self, set_frame_period,
                 set_frame_rate, get_connected_clients):
        super().__init__(canvas, send_object, send_object_to_all, start_script, restart_self, set_frame_period,
                         set_frame_rate, get_connected_clients)
        # setup
        self.logger = logging.getLogger("script:wakeuplight")
        self.set_frame_rate(1)

        # initialize required class variables
        self.current_color = Color(0, 0, 0)  # type: Color
        self.wake_time = None  # type: datetime
        self.blend_in_duration = None  # type: timedelta
        self.timezone = None
        self.delta = 0

    def update(self, canvas):
        if self.wake_time is None or self.blend_in_duration is None:
            return

        now = datetime.now(tz=self.timezone) + timedelta(minutes=self.delta)
        self.delta += 1
        if self.wake_time - self.blend_in_duration <= now <= self.wake_time + self.blend_in_duration:
            # blend-in phase
            if now < self.wake_time:
                # get percentage of activation
                wake_percentage = (self.wake_time - now).total_seconds() / self.blend_in_duration.total_seconds()
                # convert to uint8
                color_value = int(255 * (1 - wake_percentage))
                self.logger.info("{} at {}".format(color_value, now))
                # apply
                self.current_color = Color.from_single_color(color_value)
            # full-light phase
            else:
                self.current_color = Color(255, 255, 255)
        else:
            self.current_color = Color(0, 0, 0)

    def draw(self, canvas: Canvas):
        canvas.clear(self.current_color)

    def on_data(self, json, source_id):
        if "command" in json and json["command"] == "wakeuplight_set_time":
            #self.wake_time += timedelta(days=1)
            #self.wake_time.replace(hour=json["wake_hour"], minute=json["wake_minute"])
            self.timezone = pytz.timezone(json["wake_timezone"])
            self.wake_time = datetime.now(tz=self.timezone).replace(hour=22,minute=40)
            self.blend_in_duration = timedelta(minutes=json["blend_duration"])
            self.logger.info("{} with {}min".format(self.wake_time, self.blend_in_duration))
