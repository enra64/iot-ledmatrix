import random
from typing import Tuple

import copy

#from pympler.tracker import SummaryTracker

from Canvas import Canvas
from CustomScript import CustomScript
from helpers.Color import Color


def ascending(speed):
    def _ascending(particle):
        particle.y -= speed

    return _ascending


def exploding(dx, dy):
    def _exploding(particle):
        particle.x += dx
        particle.y += dy

    return _exploding


def kill_at(max_x, max_y):
    def _kill_at(particle):
        if not 0 <= particle.x < max_x or not 0 <= particle.y < max_y:
            particle.kill()

    return _kill_at


def fire_aging(amount):
    def _age(particle):
        particle.alive += amount
        particle.col.change_rgb(lambda r, g, b: (r, g * 1.04, b))

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
    def __init__(self, col: Color, position: Tuple, *strategies):
        self.x, self.y = position
        self.col = col
        self.alive = 0
        self.strategies = strategies
        self.in_use = False

    def kill(self):
        self.alive = -1  # alive -1 means dead

    def move(self):
        for s in self.strategies:
            s(self)


def smoke_machine(position, next_particle):
    colors = {0: Color(128, 128, 128),
              1: Color(80, 80, 80),
              2: Color(200, 200, 200)}

    def create():
        p = next_particle()
        p.col = random.choice(colors)
        p.x, p.y = position[0], position[1]
        p.strategies = age(1), ascending(1), fan_out(1), wind(1, 15), kill_at(10, 10)
        yield p

    while True:
        yield create()


def fire_machine(position, next_particle):
    # get 10 random fiery colors
    colors = [Color.random_color_bounded((180, 255), (80, 150), (0, 5)) for _ in range(10)]

    def create():
        behaviour = fire_aging(1), ascending(1), fan_out(1.2), wind(1, 15), kill_at(10, 10)

        c = copy.copy(random.choice(colors))

        p = Particle(c, position, *behaviour)
        yield p

    while True:
        yield create()


def random_machine(position, next_particle):
    def create():
        behaviour = age(1), ascending(1), fan_out(1), wind(1, 15), kill_at(10, 10)
        p = Particle(Color.random_color(), position, *behaviour)
        yield p

    while True:
        yield create()


def explosion_machine(position, next_particle):
    dirs = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))

    def create():
        p = next_particle()
        p.col = Color.random_color()
        p.x, p.y = position[0], position[1]
        p.strategies = exploding(*random.choice(dirs)), fan_out(.3), kill_at(10, 10)
        yield p

    while True:
        yield create()


class Emitter(object):
    def __init__(self):
        self.online_particles = []
        self.offline_particles = []
        self.factories = []

        default_color = Color()
        for _ in range(50):
            self.offline_particles.append(Particle(default_color, (0, 0), None))

    def add_factory(self, factory, pre_fill=1):
        self.factories.append(factory)
        tmp = []
        for _ in range(pre_fill):
            n = next(factory)
            tmp.extend(n)
            for p in tmp:
                p.move()
        self.online_particles.extend(tmp)

    def get_next_particle(self) -> Particle:
        return self.offline_particles.pop(0)

    def recycle_particle(self, particle):
        # move particle
        self.online_particles.remove(particle)
        self.offline_particles.append(particle)

    def update(self):
        for f in self.factories:
            new_particle = next(f)
            self.online_particles.extend(new_particle)

        for p in self.online_particles:
            p.move()
            if p.alive == -1:
                self.recycle_particle(p)

                print("%i online, %i offline" % (len(self.online_particles), len(self.offline_particles)))

    def draw(self, canvas):
        for particle in self.online_particles:
            # HINT: if you get an exception from here, the kill_at function may not be the last behaviour.
            canvas.draw_pixel(int(particle.x), int(particle.y), particle.col)


class particler(CustomScript):
    def __init__(self, canvas, send_object, send_object_to_all, start_script, restart_self, set_frame_period,
                 set_frame_rate, get_connected_clients):
        super().__init__(canvas, send_object, send_object_to_all, start_script, restart_self, set_frame_period,
                         set_frame_rate, get_connected_clients)

        self.set_frame_rate(20)

        self.emitter = Emitter()
        self.emitter.add_factory(smoke_machine((2, 9), self.emitter.get_next_particle))
        # self.emitter.add_factory(random_machine(8, 9))
        # self.emitter.add_factory(fire_machine((4, 9)))
        # self.emitter.add_factory(explosion_machine((4, 5), self.emitter.get_next_particle))
        self.frame = 0

    def update(self, canvas):
        self.frame += 1
        #if self.frame % 1000 == 0: tracker = SummaryTracker()

        self.emitter.update()
        #if self.frame % 1000 == 0: print(tracker.print_diff())

    def draw(self, canvas: Canvas):
        canvas.clear()
        self.emitter.draw(canvas)
