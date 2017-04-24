from itertools import combinations

import Canvas
from CustomScript import CustomScript
import matplotlib.pyplot as pyplot
import numpy
from itertools import product

class ThreeD_playing(CustomScript):
    def draw_cube(self):
        r = [-1, 1]
        for s, e in combinations(numpy.array(list(product(r, r, r))), 2):
            if numpy.sum(numpy.abs(s - e)) == r[1] - r[0]:
                self.ax.plot3D(*zip(s, e), color="b")

    def __init__(self, canvas, send_object, send_object_to_all, start_script, restart_self, set_frame_period,
                 set_frame_rate, get_connected_clients):
        super().__init__(canvas, send_object, send_object_to_all, start_script, restart_self, set_frame_period,
                         set_frame_rate, get_connected_clients)
        self.fig = pyplot.figure(111, figsize=(10, 10), dpi=1)
        #self.fig = pyplot.figure(111)
        #self.fig.tight_layout(pad=0)
        self.ax = self.fig.gca()
        self.draw_cube()

    def draw(self, canvas: Canvas):
        data = numpy.fromstring(self.fig.canvas.tostring_rgb(), dtype=numpy.uint8, sep='')
        data = data.reshape(self.fig.canvas.get_width_height()[::-1] + (3,))
        print("k")
        canvas.draw_numpy(0, 0, data, max_color_value=255)
