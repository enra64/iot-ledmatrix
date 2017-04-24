from random import randint, random

from Canvas import Canvas
from CustomScript import CustomScript
from helpers.Color import Color


class Particle:
    def __init__(self, x: int, y: int, dx: float, dy: float, canvas_width:int, canvas_height:int, life: int = 4, color: Color = Color(255)):
        self.color = color
        self.x = x
        self.y = y
        self.old_x = x
        self.old_y = y
        self.dx = dx
        self.dy = dy
        self.life = life
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height
        self.luminance = self.color.get_hls()[0]
        self.blank_old_location = False
        #print("adding particle at " + str(x) + "," + str(y) + ", delta" + str(dx) + "," + str(dy))

    def update(self):
        self.old_x = self.x
        self.old_y = self.y
        self.x += self.dx
        self.y += self.dy

        if int(self.old_x) != int(self.x) or int(self.old_y) != int(self.y):
            self.blank_old_location = True

        self.life -= 1
        self.luminance *= 0.8
        self.color.set_luminance(self.luminance)

    def draw(self, canvas):
        if self.is_alive():
            canvas.draw_pixel(int(self.x), int(self.y), self.color)
            #if self.blank_old_location and self.old_on_screen(): canvas.draw_pixel(int(self.old_x), int(self.old_y), Color(0, 0, 0))

    def old_on_screen(self):
        return 0 <= self.old_x < self.canvas_width and 0 <= self.old_y < self.canvas_height

    def on_screen(self):
        return 0 <= self.x < self.canvas_width and 0 <= self.y < self.canvas_height

    def is_alive(self):
        return self.on_screen() and self.luminance > 0.1


class SpawnPoint:
    def create_particle(self):
        dx = (random() - 0.5) * 2
        dy = (random() - 0.5) * 2
        self.particles.append(Particle(self.x, self.y, dx, dy, self.canvas_width, self.canvas_height, life=4, color=self.color))

    def __init__(self, x: int, y: int, color: Color, canvas_width: int, canvas_height: int, life:int = 20):
        self.life = life
        self.x = x
        self.y = y
        self.color = color
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height
        self.next_spawn_mod = randint(1, 7)
        self.particles = []
        self.frame = 0
        self.has_live_particles = True
        self.create_particle()

    def update(self, canvas):
        # only spawn new particles while alive
        self.frame += 1
        if self.life > 0 and self.frame % self.next_spawn_mod == 0:
            self.next_spawn_mod = randint(1, 7)
            self.frame = 0
            self.create_particle()

        self.has_live_particles = False
        for particle in self.particles:
            particle.update()

            if particle.is_alive():
                self.has_live_particles = True

        self.life -= 1

    def draw(self, canvas):
        for particle in self.particles:
            particle.draw(canvas)

    def is_alive(self):
        return self.has_live_particles


class particler(CustomScript):
    def __init__(self, canvas, send_object, send_object_to_all, start_script, restart_self, set_frame_period,
                 set_frame_rate, get_connected_clients):
        super().__init__(canvas, send_object, send_object_to_all, start_script, restart_self, set_frame_period,
                         set_frame_rate, get_connected_clients)
        self.frame = 0
        self.spawners = []

        self.set_frame_period(.15)

        x = randint(0, canvas.width)
        y = randint(0, canvas.height)
        self.spawners.append(SpawnPoint(x, y, Color.random_color(), canvas.width, canvas.height))


    def update(self, canvas):
        self.frame += 1
        if self.frame == 12:
            self.frame = 0
            x = randint(0, canvas.width)
            y = randint(0, canvas.height)
            self.spawners.append(SpawnPoint(x, y, Color.random_color(), canvas.width, canvas.height))

        for spawner in self.spawners:
            spawner.update(canvas)

        self.spawners = [spawner for spawner in self.spawners if spawner.is_alive()]

    def draw(self, canvas: Canvas):
        for spawner in self.spawners:
            spawner.draw(canvas)
