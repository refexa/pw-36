# -*- coding: utf-8 -*-
import logging
import random
from dataclasses import dataclass
from typing import List

from pygame.math import Vector3 as Vector

from game import tweening

logger = logging.getLogger(__name__)
logger.debug("importing...")


class Behavior:
    # def __init__(self, tweener):
    #     self._tweener = tweener

    @staticmethod
    def process(group, world):
        logger.debug("Processing behavior")

    def _cb(self, *args):
        pass


z_axis = Vector(0, 0, 1)


class EasyBehavior(Behavior):
    @staticmethod
    def process(group, world):
        # logger.debug("Processing behavior easy")
        # this is only called once
        world.start_timer(EasyBehavior.on_timer, 1, False, (group, world))

    @staticmethod
    def on_timer(timer):
        group, world = timer.data
        if group.entities:
            e = group.entities[0]
            half_x = 150
            half_y = 150
            px = random.randrange(int(e.position.x - half_x), int(e.position.x + half_x))
            py = random.randrange(int(e.position.y - half_y), int(e.position.y + half_y))
            direction = Vector(px, py, 0) - e.position
            dist = direction.length()
            speed = 90
            duration = dist / speed
            for e in group.entities:
                world._tweener.create_tween_by_end(e, "position", e.position, e.position + direction, duration,
                                                   ease_function=tweening.ease_in_out_quad)
            timer.interval = duration


class MediumBehavior(Behavior):
    @staticmethod
    def process(group, world):
        # logger.debug("Processing behavior medium")
        # this is only called once
        world.start_timer(MediumBehavior.on_timer, 1, False, (group, world))

    @staticmethod
    def on_timer(timer):
        group, world = timer.data
        if group.entities:
            e = group.entities[0]
            half_x = 50
            half_y = 150
            px = random.randrange(int(e.position.x - half_x), int(e.position.x + half_x))
            # py = random.randrange(int(e.position.y - half_y), int(e.position.y + half_y))
            py = e.position.y + 0.75 * (world._level.ship.position.y - e.position.y)
            direction = Vector(px, py, 0) - e.position
            dist = direction.length()
            speed = 50
            duration = dist / speed
            for e in group.entities:
                world._tweener.create_tween_by_end(e, "position", e.position, e.position + direction, duration,
                                                   ease_function=tweening.ease_in_out_quad)
            timer.interval = duration


class HardBehavior(Behavior):
    @staticmethod
    def process(group, world):
        # logger.debug("Processing behavior hard")
        # this is only called once
        world.start_timer(HardBehavior.on_timer, 1, False, (group, world))

    @staticmethod
    def on_timer(timer):
        group, world = timer.data
        if group.entities:
            e = group.entities[0]
            half_x = 30
            half_y = 30
            px = random.randrange(int(e.position.x - half_x), int(e.position.x + half_x))
            py = random.randrange(int(e.position.y - half_y), int(e.position.y + half_y))
            direction = Vector(px, py, 0) - e.position
            dist = direction.length()
            speed = 30
            duration = dist / speed
            for e in group.entities:
                world._tweener.create_tween_by_end(e, "position", e.position, e.position + direction, duration,
                                                   ease_function=tweening.ease_in_out_quad)
            timer.interval = duration

            ship_angle = (world._level.ship.position - e.position).angle_to(world.x_axis)
            da = ship_angle - e.angle
            e.angle += da
            for c in e.cannons:
                c.heading.rotate_ip(da, z_axis)
            # angle = cannon.heading.angle_to(x_axis)
            # if cannon.heading.y < 0:
            #     angle = 360 - angle
            #
            # bullet.angle = -angle


@dataclass
class Group:
    entities: List
    behavior_type: type
    active: bool = False

    def activate(self, game_scene):
        if self.active:
            return
        self.active = True
        # start behavior
        self.behavior_type.process(self, game_scene)


logger.debug("imported")
