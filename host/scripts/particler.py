import random
from typing import Tuple

import copy

from Canvas import Canvas
from CustomScript import CustomScript
from helpers.Color import Color


def ascending(speed):
    def _ascending(particle):
        particle.y -= speed

    return _ascending


def kill_at(max_x, max_y):
    def _kill_at(particle):
        if not 0 <= particle.x < max_x or not 0 <= particle.y < max_y:
            particle.kill()

    return _kill_at

def fire_aging(amount):
    def _age(particle):
        particle.alive += amount
        particle.col.change_rgb(lambda r, g, b: (r, g * 1.05, b))

    return _age

def age(amount):
    def _age(particle):
        particle.alive += amount

    return _age


def fan_out(modifier):
    """
    
    :param modifier: larger values create more fanout. try ~0-2. 
    :return: 
    """
    def _fan_out(particle):
        addition = random.random() * modifier - (modifier / 2)
        particle.x += addition

    return _fan_out


def wind(direction, strength):
    def _wind(particle):
        if random.randint(0, 100) < strength:
            particle.x += direction

    return _wind


class Particle:
    def __init__(self, col: Color, size: int, position: Tuple, *strategies):
        self.x, self.y = position
        self.col = col
        self.alive = 0
        self.strategies = strategies
        self.size = size

    def kill(self):
        self.alive = -1  # alive -1 means dead

    def move(self):
        for s in self.strategies:
            s(self)


def smoke_machine(position):
    colors = {0: Color(128, 128, 128),
              1: Color(80, 80, 80),
              2: Color(200, 200, 200)}

    def create():
        behaviour = age(1), ascending(1), fan_out(1), wind(1, 15), kill_at(10, 10)
        p = Particle(random.choice(colors), random.randint(10, 15), position, *behaviour)
        yield p

    while True:
        yield create()

def fire_machine(position):
    # get 10 random fiery colors
    colors = [Color.random_color_bounded((180, 255), (80, 150), (0, 5)) for _ in range(10)]

    def create():
        behaviour = fire_aging(1), ascending(1), fan_out(1.2), wind(1, 15), kill_at(10, 10)

        c = copy.copy(random.choice(colors))

        p = Particle(c, random.randint(10, 15), position, *behaviour)
        yield p

    while True:
        yield create()

def random_machine(x, y):
    def create():
        behaviour = age(1), ascending(1), fan_out(1), wind(1, 15), kill_at(10, 10)
        p = Particle(Color.random_color(), random.randint(10, 15), (x, y), *behaviour)
        yield p

    while True:
        yield create()

class Emitter(object):
    def __init__(self):
        self.particles = []
        self.factories = []

    def add_factory(self, factory, pre_fill=1):
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

        self.set_frame_rate(20)

        self.emitter = Emitter()
        #self.emitter.add_factory(smoke_machine((2, 9)))
        #self.emitter.add_factory(random_machine(8, 9))
        self.emitter.add_factory(fire_machine((4, 9)))

    def update(self, canvas):
        self.emitter.update()

    def draw(self, canvas: Canvas):
        self.emitter.draw(canvas)
