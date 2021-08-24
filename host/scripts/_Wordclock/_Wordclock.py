import json
import logging
import time
from datetime import datetime
from json import JSONDecodeError

from Canvas import Canvas
from CustomScript import CustomScript
from scripts._Wordclock import ColorLogic
from scripts._Wordclock.Settings import Settings
from scripts._Wordclock.WordLogic import WordLogic


class _Wordclock(CustomScript):
    def __init__(self, canvas, send_object, send_object_to_all, start_script, restart_self, set_frame_period,
                 set_frame_rate, get_connected_clients):
        super().__init__(canvas, send_object, send_object_to_all, start_script, restart_self, set_frame_period,
                         set_frame_rate, get_connected_clients)
        self.logger = logging.getLogger("script:wordclock")

        config_file_path = self.find_word_config_file("assets/wordclock_config_selector.json")

        self.color_config_path = "wordclock_color_config.json"
        self.logger.info("using {} and {} as config".format(config_file_path, self.color_config_path))
        self.enable = True
        self.last_visible_on_pir = None

        try:
            self.word_logic = WordLogic(config_file_path)
            ColorLogic.read_color_config_file(self.color_config_path, self.word_logic.get_all_words())
            self.settings = Settings()
        except Exception as e:
            raise e
        else:
            self.__send_config()
            self.rectangles = []

            self.set_frame_rate(1)

        self.pir = None
        if self.settings.enable_pir():
            from scripts._Wordclock.PirSensor import PirSensor
            self.pir = PirSensor(self.settings.get_pir_sensor_pin())

    def find_word_config_file(self, wordclock_config_file: str):
        try:
            with open(wordclock_config_file, "r", encoding="utf-8") as in_file:
                return json.load(in_file)["wordclock_config_file"]
        except FileNotFoundError:
            self.logger.info("no wordclock config location found in {}. you must create it!".format(wordclock_config_file))
        except JSONDecodeError:
            self.logger.error("bad wordclock config location {}!".format(wordclock_config_file))

    def __get_current_time(self) -> datetime:
        """Helper function for getting the correct time"""
        #return datetime.strptime("11:30", '%H:%M')
        return datetime.now()

    def __check_pir_recommends_enabling(self):
        if not self.settings.enable_pir():
            return True
        else:
            pir_visible = self.pir.is_something_visible()
            if pir_visible:
                self.last_visible_on_pir = time.time()

            return time.time() - self.last_visible_on_pir <= 120

    def update(self, canvas):
        time = self.__get_current_time()

        self.enable = self.settings.is_time_within_limit(time.hour) and self.__check_pir_recommends_enabling()

        if self.settings.should_randomize_colors(time):
            ColorLogic.randomize_colors(self.word_logic.get_all_words(), self.color_config_path)
            self.__send_config()

        if self.enable:
            self.rectangles = self.word_logic.get_current_rectangles(time, canvas)

    def draw(self, canvas: Canvas):
        canvas.clear()

        if self.enable:
            for rectangle in self.rectangles:
                canvas.draw_rectangle(rectangle)

    def __send_config(self):
        color_config = ColorLogic.get_color_config(self.word_logic.get_all_words())
        self.send_object_to_all(
            {
                "message_type": "wordclock_configuration",
                "config": self.word_logic.get_config()["config"],
                "lines": self.word_logic.get_config()["lines"],
                "color_config": color_config,
                "settings": self.settings.get_configuration_dict()
            })

    def on_client_connected(self, id):
        self.__send_config()

    def on_data(self, json, source_id):
        if "command" in json and json["command"] == "retry sending wordclock config":
            self.__send_config()
        elif "word_color_config" in json:
            color_array = json["word_color_config"]
            ColorLogic.update_color_info(color_array, self.word_logic.get_all_words())
            ColorLogic.save_color_info(self.color_config_path, color_array)
        elif json["command"] == "update_settings":
            settings = json["settings"]
            self.settings.set_configuration_dict(settings, self.__get_current_time())
        else:
            self.logger.error("wordclock script received unrecognized data: {}".format(json))
