import logging
from typing import Optional

import pytz
from pyparsing import col

import Canvas
from CustomScript import CustomScript
from datetime import datetime, timedelta

from helpers.Button import Button
from helpers.Color import Color


class _WakeUpLight(CustomScript):
    def __init__(self, canvas, send_object, send_object_to_all, start_script, restart_self, set_frame_period,
                 set_frame_rate, get_connected_clients):
        super().__init__(canvas, send_object, send_object_to_all, start_script, restart_self, set_frame_period,
                         set_frame_rate, get_connected_clients)
        # setup
        self.logger = logging.getLogger("script:wakeuplight")
        self.set_frame_rate(.1)
        self._force_switch = Button(17, bouncetime=100)
        self._force_switch.register()

        # initialize required class variables
        self._clear_properties()

    def _clear_properties(self):
        self.current_color = Color(0, 0, 0)  # type: Color
        self.timezone = None  # pytz.timezone("Europe/Berlin")
        self.wake_time = None  # datetime.now(tz=self.timezone).replace(hour=20, minute=10)  # type: datetime
        self.blend_in_duration = None  # timedelta(minutes=30)  # type: timedelta
        self.time_delta = 0  # type: int
        self.lower_color_temperature = 1800  # type: int
        self.upper_color_temperature = 2800  # type: int
        self.test_color_temperature = None  # type: Optional[int]
        self.enable_color_temp_test = False  # type: bool

    def update(self, canvas):
        if self.enable_color_temp_test:
            self.current_color = Color.from_temperature(self.test_color_temperature, 1)
            return

        if self._force_switch.is_high():
            self.current_color = Color.from_temperature(4000, 1)

        if self.wake_time is None or self.blend_in_duration is None:
            return

        now = datetime.now(tz=self.timezone) + timedelta(minutes=self.time_delta)
        #self.time_delta += 1
        if self.wake_time - self.blend_in_duration <= now <= self.wake_time + self.blend_in_duration:
            # blend-in phase
            light_percentage = 1
            if now < self.wake_time:
                light_percentage = 1 - ((self.wake_time - now).total_seconds() / self.blend_in_duration.total_seconds())

            # convert to uint8
            color_temp = self.lower_color_temperature + (self.upper_color_temperature - self.lower_color_temperature) * light_percentage
            color_value = Color.from_temperature(color_temp, light_percentage)
            color_value.set_value(light_percentage)

            self.logger.info("{} at {}".format(color_value, now))
            # apply
            self.current_color = color_value
        else:
            self.current_color = Color(0, 0, 0)

    def draw(self, canvas: Canvas):
        canvas.clear(self.current_color)

    def on_data(self, json, source_id):
        if "command" in json and json["command"] == "wakeuplight_set_time":
            self.timezone = pytz.timezone(json["wake_timezone"])
            self.wake_time = datetime.now(tz=self.timezone).replace(hour=json["wake_hour"], minute=json["wake_minute"])
            now = datetime.now(tz=self.timezone) + timedelta(minutes=self.time_delta)
            if self.wake_time.time() < now.time():
                self.wake_time += timedelta(days=1)

            self.blend_in_duration = timedelta(minutes=json["blend_duration"])
            self.lower_color_temperature = json["lower_color_temperature"]
            self.upper_color_temperature = json["upper_color_temperature"]
            if self.enable_color_temp_test:
                self.set_frame_rate(1)
                self.enable_color_temp_test = False
            self.logger.info("{} with {}min".format(self.wake_time, self.blend_in_duration))
            self.send_object({
                'message_type': 'wakeuplight_ack',
                'msg_identifier': "set:{}:{}".format(json['wake_hour'], json['wake_minute'])
            }, source_id)
        elif "command" in json and json["command"] == "clear_wakeup_time":
            self._clear_properties()
            self.send_object({
                'message_type': 'wakeuplight_ack',
                'msg_identifier': "clear:"
            }, source_id)
            self.logger.info("Cleared wakeup time")
        elif "command" in json and json["command"] == "test_color_temperature":
            self.test_color_temperature = json["color_temperature"]
            self.enable_color_temp_test = True
            self.set_frame_rate(30)
