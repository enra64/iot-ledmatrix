from Canvas import Canvas
from CustomScript import CustomScript
from helpers.Color import Color


class _ScrollingText(CustomScript):
    def __init__(self, canvas, send_object, send_object_to_all, start_script, restart_self, set_frame_period,
                 set_frame_rate, get_connected_clients):
        super().__init__(canvas, send_object, send_object_to_all, start_script, restart_self, set_frame_period,
                         set_frame_rate, get_connected_clients)
        self.current_x = 0
        self.current_text = None
        self.current_color = Color(255, 255, 255)
        self.current_text_width = None
        self.canvas_width = canvas.width

        canvas.set_font("helvetica.otf", 8)

    def draw(self, canvas: Canvas):
        canvas.clear()
        if self.current_text is not None and self.current_color is not None:
            self.current_text_width = canvas.draw_text(self.current_text, self.current_x, 0, self.current_color)

    def on_data(self, data_dictionary, source_id):
        command = data_dictionary['command']
        if command == "change_text":
            self.current_text = data_dictionary['text']
            self.current_x = self.canvas_width
        elif command == "change_color":
            self.current_color = Color.from_rgb(data_dictionary['color'])
        elif command == "change_speed":
            speed = data_dictionary['speed']
            self.set_frame_rate(speed * 2)
        else:
            print("unknown command")

    def update(self, canvas):
        self.current_x -= 1

        # wrap around matrix borders
        if self.current_text_width is not None and self.current_x + self.current_text_width < 0:
            self.current_x = self.canvas_width

