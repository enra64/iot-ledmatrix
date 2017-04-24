from random import randint, choice

from Canvas import Canvas
from CustomScript import CustomScript
from helpers.Color import Color


class Particle():
    def __init__(self, col, size, *strategies):
        self.x, self.y = 0, 0
        self.col = col
        self.alive = 0
        self.strategies = strategies
        self.size = size

    def kill(self):
        self.alive = -1  # alive -1 means dead

    def move(self):
        for s in self.strategies:
            s(self)


def ascending(speed):
    def _ascending(particle):
        particle.y -= speed

    return _ascending


def kill_at(max_x, max_y):
    def _kill_at(particle):
        if not 0 <= particle.x < max_x or not 0 <= particle.y < max_y:
            particle.kill()

    return _kill_at


def age(amount):
    def _age(particle):
        particle.alive += amount

    return _age


def fan_out(modifier):
    def _fan_out(particle):
        d = particle.alive / modifier
        d += 1
        particle.x += randint(0, 2 * int(d)) - d

    return _fan_out


def wind(direction, strength):
    def _wind(particle):
        if randint(0, 100) < strength:
            particle.x += direction

    return _wind


def smoke_machine():
    colors = {0: Color(128, 128, 128),
              1: Color(80, 80, 80),
              2: Color(200, 200, 200)}

    def create():
        #for _ in range(choice([0, 0, 0, 0, 0, 0, 0, 1, 2, 3])):
        behaviour = age(1), ascending(1), fan_out(400), wind(1, 15), kill_at(10, 10)
        p = Particle(colors[randint(0, 2)], randint(10, 15), *behaviour)
        yield p

    while True:
        yield create()


class Emitter(object):
    def __init__(self, pos=(0, 0)):
        self.particles = []
        self.pos = pos
        self.factories = []

    def add_factory(self, factory, pre_fill=5):
        self.factories.append(factory)
        tmp = []
        for _ in range(pre_fill):
            n = next(factory)
            tmp.extend(n)
            for p in tmp:
                p.move()
        self.particles.extend(tmp)

    def update(self):
        for f in self.factories:
            new_particle = next(f)
            self.particles.extend(new_particle)

        for p in self.particles[:]:
            p.move()
            if p.alive == -1:
                self.particles.remove(p)

    def draw(self, canvas):
        for ptcl in self.particles:
            canvas.draw_pixel(int(ptcl.x), int(ptcl.y), ptcl.col)


class particler(CustomScript):
    def __init__(self, canvas, send_object, send_object_to_all, start_script, restart_self, set_frame_period,
                 set_frame_rate, get_connected_clients):
        super().__init__(canvas, send_object, send_object_to_all, start_script, restart_self, set_frame_period,
                         set_frame_rate, get_connected_clients)

        self.emitter = Emitter((4, 9))
        self.emitter.add_factory(smoke_machine())

    def update(self, canvas):
        self.emitter.update()

    def draw(self, canvas: Canvas):
        self.emitter.draw(canvas)
