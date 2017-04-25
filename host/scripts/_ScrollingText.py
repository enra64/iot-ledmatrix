from Canvas import Canvas
from CustomScript import CustomScript
from helpers.Color import Color
from helpers.TextScroller import TextScroller


class _ScrollingText(CustomScript):
    def __init__(self, canvas, send_object, send_object_to_all, start_script, restart_self, set_frame_period,
                 set_frame_rate, get_connected_clients):
        super().__init__(canvas, send_object, send_object_to_all, start_script, restart_self, set_frame_period,
                         set_frame_rate, get_connected_clients)
        self.text_scroller = TextScroller(canvas)

    def draw(self, canvas: Canvas):
        self.text_scroller.draw(canvas, clear=True)

    def on_data(self, data_dictionary, source_id):
        command = data_dictionary['command']
        if command == "change_text":
            self.text_scroller.set_text(data_dictionary['text'])
        elif command == "change_color":
            self.text_scroller.set_color(Color.from_rgb(data_dictionary['color']))
        elif command == "change_speed":
            speed = data_dictionary['speed']
            self.set_frame_rate((speed + 1) * 2)
        elif command == "set_font_size":
            self.text_scroller.set_size(data_dictionary['size'])
        else:
            print("unknown command")

    def update(self, canvas):
        self.text_scroller.update()
