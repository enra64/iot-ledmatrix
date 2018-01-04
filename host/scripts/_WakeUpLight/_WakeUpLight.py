import logging

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
        self.set_frame_rate(.1)

        # initialize required class variables
        self.current_color = Color(0, 0, 0)  # type: Color
        self.wake_time = None  # type: datetime
        self.blend_in_duration = None  # type: timedelta

    def update(self, canvas):
        if self.wake_time is None or self.blend_in_duration is None:
            return

        now = datetime.now()
        if self.wake_time - self.blend_in_duration <= now <= self.wake_time + self.blend_in_duration:
            # blend-in phase
            if now < self.wake_time:
                # get percentage of activation
                wake_percentage = (self.wake_time - now).total_seconds() / self.blend_in_duration.total_seconds()
                # apply
                self.current_color = Color.from_single_color(int(255 * wake_percentage))
            # full-light phase
            else:
                self.current_color = Color(255, 255, 255)
        else:
            self.current_color = Color(0, 0, 0)

    def draw(self, canvas: Canvas):
        canvas.clear(self.current_color)