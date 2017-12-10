import datetime
import logging
from typing import List

from Canvas import Canvas, Rect
from CustomScript import CustomScript
from scripts._Wordclock import ColorLogic
from scripts._Wordclock.WordLogic import WordLogic


class _Wordclock(CustomScript):
    def __init__(self, canvas, send_object, send_object_to_all, start_script, restart_self, set_frame_period,
                 set_frame_rate, get_connected_clients):
        super().__init__(canvas, send_object, send_object_to_all, start_script, restart_self, set_frame_period,
                         set_frame_rate, get_connected_clients)
        self.logger = logging.getLogger("script:wordclock")
        self.debug_time_offset = 0

        # config_file_path = "assets/arnes_wordclock_config.json"
        # config_file_path = "assets/config_ledmatrix_arnes_wordclock_lines_filled_with_other_letters.json"
        # config_file_path = "assets/merets_wordclock_config.json"
        config_file_path = "assets/susannes_wordclock_config.json"
        self.color_config_path = "wordclock_color_config.json"
        self.logger.info("using {} and {} as config".format(config_file_path, self.color_config_path))

        try:
            self.word_logic = WordLogic(config_file_path)
            ColorLogic.read_color_config_file(self.color_config_path, self.word_logic.get_all_words())
        except Exception as e:
            raise e
        else:
            self.__send_config()
            self.rectangles = []

            self.set_frame_rate(24)

    def update(self, canvas):
        offset_time = datetime.datetime.now() + datetime.timedelta(minutes=self.debug_time_offset)
        self.rectangles = self.word_logic.get_current_rectangles(offset_time, canvas)

        # debugging
        def print_time(time):
            formatted_time = ":".join(str(time).split()[1].split(".")[0].split(":")[:3])
            self.logger.info("showing time {}".format(formatted_time))

        def debug_print_rectangles(word_rectangles: List[Rect]):
            for rectangle in word_rectangles:
                self.logger.info(
                    "rect at <{}, {}> size [{}, {}]".format(rectangle.x, rectangle.y, rectangle.width, rectangle.height))

        print_time(offset_time)
        self.debug_time_offset += 0

    def draw(self, canvas: Canvas):
        canvas.clear()
        for rectangle in self.rectangles:
            canvas.draw_rectangle(rectangle)

    def __send_config(self):
        self.send_object_to_all(
            {
                "message_type": "wordclock_configuration",
                "config": self.word_logic.get_config()["config"],
                "lines": self.word_logic.get_config()["lines"]
            })
        self.send_object_to_all(
            {
                "message_type": "wordclock_color_configuration",
                "color_config": ColorLogic.get_color_config(self.word_logic.get_all_words())
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
