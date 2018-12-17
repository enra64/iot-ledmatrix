import json
import logging
from datetime import datetime
from typing import Dict


class Settings:
    def __init__(self):
        try:
            with open("wordclockconfig.json", "r", encoding="utf-8") as settings_file:
                self.settings = json.load(settings_file)
        except FileNotFoundError:
            self.settings = {
                "limit_display_time": True,
                "display_time_start_h": 6,
                "display_time_stop_h": 2,
                "randomization_enabled": True,
                "randomization_interval": 1,
            }

        self.last_randomization_timestamp = None
        self.logger = logging.getLogger("wordclock:settings")

    def is_time_within_limit(self, time: int) -> bool:
        """
        Return True iff display should be enabled at the current time
        :param time: the time in hours
        :return: True iff display should be enabled at the current time
        """
        if not self.settings["limit_display_time"] or self.settings["display_time_start_h"] == self.settings["display_time_stop_h"]:
            return True

        stop_is_next_day = self.settings["display_time_stop_h"] < self.settings["display_time_start_h"]

        if stop_is_next_day:
            return time >= self.settings["display_time_start_h"] or time < self.settings["display_time_stop_h"]
        else:
            return self.settings["display_time_start_h"] <= time < self.settings["display_time_stop_h"]

    def enable_pir(self) -> bool:
        return self.settings.get("enable_pir", False)

    def get_current_interval(self, time: datetime):
        interval_setting = self.settings["randomization_interval"]

        if interval_setting == 0:
            return time.hour
        elif interval_setting == 1:
            return time.day
        elif interval_setting == 2:
            return time.isocalendar()[1]  # week number
        elif interval_setting == 3:
            return time.month
        else:
            self.logger.error("unknown color randomization interval: {}".format(interval_setting))

    def should_randomize_colors(self, time: datetime) -> bool:
        if not self.settings["randomization_enabled"]:
            return False

        now = self.get_current_interval(time)

        # only randomize if the timestamp has changed
        if now != self.last_randomization_timestamp:
            self.last_randomization_timestamp = now
            return True

        return False

    def get_configuration_dict(self) -> Dict:
        return self.settings

    def set_configuration_dict(self, settings: Dict, time: datetime):
        self.settings = settings
        with open("wordclockconfig.json", "w") as settings_file:
            json.dump(settings, settings_file)

        # set last randomization interval to now to avoid instantly randomizing
        self.last_randomization_timestamp = self.get_current_interval(time)
