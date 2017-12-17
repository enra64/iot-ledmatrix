import json

import datetime
from typing import Dict


class Settings:
    def __init__(self):
        try:
            with open("wordclockconfig.json", "r") as settings_file:
                self.settings = json.load(settings_file)
        except FileNotFoundError:
            self.settings = {
                "limit_display_time": True,
                "display_time_start_h": 6,
                "display_time_stop_h": 2,
            }

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

    def get_configuration_dict(self) -> Dict:
        return self.settings
