from CustomScript import CustomScript
from canvas import Canvas

class flashlight(CustomScript):
    def __init__(self, canvas, send_object, send_object_to_all, start_script):
        super().__init__(canvas, send_object, send_object_to_all, start_script)
        self.enable = True

    def draw(self, canvas: Canvas):
        if self.enable:
            canvas.clear(255, 255, 255)
        else:
            canvas.clear(0, 0, 0)

    def on_data(self, json, source_id):
        if 'enable' in json:
            self.enable = json['enable']
