from helpers.Color import Color

from CustomScript import CustomScript
from Canvas import Canvas


class _SimpleDrawing(CustomScript):
    def __init__(self, canvas, send_object, send_object_to_all, start_script, restart_self, set_frame_period,
                 set_frame_rate, get_connected_clients):
        super().__init__(canvas, send_object, send_object_to_all, start_script, restart_self, set_frame_period,
                         set_frame_rate, get_connected_clients)
        self.client_data = None
        canvas.clear()

    def on_data(self, received_object, source_id):
        self.client_data = received_object['color_array']

    def draw(self, canvas: Canvas):
        if self.client_data is not None:
            for x in range(0, canvas.width):
                for y in range(0, canvas.height):
                    color = Color(
                        self.client_data[x][y][0],
                        self.client_data[x][y][1],
                        self.client_data[x][y][2]
                    )
                    canvas.draw_pixel(x, y, color)
