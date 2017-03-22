from matgraphics import Canvas

class simple_drawing:
    def __init__(self, canvas, send_object, send_object_to_all, start_script):
        self.client_data = None
        canvas.clear()

    def update(self, canvas):
        pass

    def on_data(self, recv_json, source_id):
        self.client_data = recv_json['color_array']

    def draw(self, canvas: Canvas):
        if self.client_data is not None:
            for x in range(0, canvas.width):
                for y in range(0, canvas.height):
                    canvas.draw_pixel(x, y, self.client_data[x][y][0], self.client_data[x][y][1], self.client_data[x][y][2])

        #print(repr(canvas))

    def exit(self):
        pass
