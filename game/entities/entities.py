# -*- coding: utf-8 -*-
import logging
import typing
from dataclasses import dataclass
from types import MethodType as _MethodType
from weakref import WeakMethod as _WeakMethod
from weakref import ref as _ref

import pygame
from pygame.math import Vector3 as Vector

from game.resourcegame import res_id_cannon, res_id_friend_bullet, res_id_enemy_bullet, res_id_ship, res_id_powerup, \
    res_id_mine, \
    res_id_enemy_easy, res_id_enemy_medium, res_id_enemy_hard, res_id_enemy_hard_bullet, res_id_enemy_medium_bullet

logger = logging.getLogger(__name__)
logger.debug("importing...")


class TimerData:
    _next_id = 0
    def __init__(self, func: typing.Callable, interval: float, next_time: float = 0, data: typing.Any = None):
        self.func = self._make_weakref(func)
        self.interval = interval  # set this to 0 if you want to stop the timer within the callback
        self.data = data
        self.next_time = next_time
        self.id = self._next_id
        TimerData._next_id += 1

    def remaining(self, game_time_now):
        """Returns the remaining time to next execution in seconds.
        Negative values mean that it is overdue and will be this time span too late."""
        return self.next_time - game_time_now

    @staticmethod
    def _make_weakref(func):
        if isinstance(func, _MethodType):
            return _WeakMethod(func)
        else:
            return _ref(func)


class _Visible:  # this is just a template with the attributes needed to draw it
    # image
    resource_id = 1
    layer = 0
    # animation
    idx = 0
    next_time = 0
    fps = 10
    loop = True
    end_cb = None  # signature: cb(cb_data, draw_list)  # will only be called with loop=False
    cb_data = None
    special_draw_func = None  # signature: draw( screen, camera, self, resource_map )
    # position and orientation
    position = [0, 0, 1]
    angle = 0  # degrees
    flip_x = False
    flip_y = False
    scale = 1  # 0.0 < zoom in 0.1 steps
    alpha = 1  # 0.0 <= alpha <= 1.0


class Cannon(_Visible):
    resource_id = res_id_cannon

    def __init__(self, heading):
        self.firing = False
        self.interval = 0.1
        self.heading = heading
        self.timer_id = -1


@dataclass
class _CollisionEntity:
    position: Vector
    radius: float
    angle: float


@dataclass
class Portal(_CollisionEntity, _Visible):
    resource_id: typing.Any


class FBulletTemplate:
    resource_id = res_id_friend_bullet
    speed = 300
    radius = 5
    angle = 0


class EBulletTemplate:
    resource_id = res_id_enemy_bullet
    speed = 300
    radius = 5
    angle = 0


class EMediumBulletTemplate:
    resource_id = res_id_enemy_medium_bullet
    speed = 150
    radius = 10
    angle = 0


class EHardBulletTemplate:
    resource_id = res_id_enemy_hard_bullet
    speed = 500
    radius = 5
    angle = 0


class Bullet(_CollisionEntity, _Visible):
    layer = 30

    def __init__(self, template, position, direction, source):
        super().__init__(position, template.radius, template.angle)
        self.source = source
        self.resource_id = template.resource_id
        self.velocity = direction * template.speed


class Ship(_CollisionEntity, _Visible):
    resource_id = res_id_ship
    layer = 100

    def __init__(self, cannons: typing.List[Cannon], position, radius, angle=0):
        super().__init__(position, radius, angle)
        self.direction = Vector(0, 0, 0)
        self.rect = pygame.Rect(0, 0, 2 * radius, 2 * radius)
        self.cannons = cannons

        # todo: dark matter as a player resource
        # Thoughts:
        # - Shield is depleted by 1 every time the ship is involved in a collision
        # - When shield is 0, 1 collision will destroy the ship
        # - Shield recharges at 2 points per second
        # - Shield recharge consumes dark matter, 1:1; shield cannot recharge without dark matter
        # - BKB replenishes dark matter; gain may be fixed or variable; try it and see which is best
        # - RKB depletes dark matter; loss may be fixed or variable; try it and see which is best
        # - BKB and RKB may be found floating, or drop randomly from destroyed enemies
        self.shields = 20
        self.shields_max = 20
        self.dark_matter = 100
        self.dark_matter_max = 100


class PowerUp(_CollisionEntity, _Visible):
    resource_id = res_id_powerup
    amount = 10
    layer = 20

    def __init__(self, position, radius, angle=0):
        super().__init__(position, radius, angle)


class Mine(_CollisionEntity, _Visible):
    resource_id = res_id_mine
    amount = 10
    layer = 25

    def __init__(self, position, radius, angle=0):
        super().__init__(position, radius, angle)


class _Enemy(_CollisionEntity, _Visible):

    def __init__(self, cannons: typing.List[Cannon], position, radius, angle, group_id):
        super().__init__(position, radius, angle)
        self.cannons = cannons
        self.velocity = Vector(0, 0, 0)
        self.group_id = group_id


class EnemyEasy(_Enemy):
    resource_id = res_id_enemy_easy
    layer = 40

    def __init__(self, cannons: typing.List[Cannon], position, radius, group_id, angle=0):
        super().__init__(cannons, position, radius, angle, group_id)


class EnemyMedium(_Enemy):
    resource_id = res_id_enemy_medium
    layer = 41

    def __init__(self, cannons: typing.List[Cannon], position, radius, group_id, angle=0):
        super().__init__(cannons, position, radius, angle, group_id)


class EnemyHard(_Enemy):
    resource_id = res_id_enemy_hard
    layer = 42

    def __init__(self, cannons: typing.List[Cannon], position, radius, group_id, angle=0):
        super().__init__(cannons, position, radius, angle, group_id)


_z_axis = Vector(0, 0, 1)


class Wall(_Visible):
    layer = 0

    def __init__(self, start_point, end_point, points):
        self.points = points
        self.start_point = start_point
        self.end_point = end_point
        self.diff: Vector = (end_point - start_point)
        self.direction = self.diff.normalize()
        self.normal = self.diff.rotate(90, _z_axis).normalize()
        points_x = [p.x for p in self.points]
        points_y = [p.y for p in self.points]
        x_min = min(points_x)
        y_min = min(points_y)
        x_max = max(points_x)
        y_max = max(points_y)
        self.rect = pygame.Rect(x_min, y_min, x_max - x_min, y_max - y_min)
        self.rect.normalize()


class SpecialDraw(_Visible):

    def __init__(self, special_draw_func, layer=0):
        self.special_draw_func = special_draw_func
        self.layer = layer


def remove_after_animation(data, entities: typing.List, *args):
    try:
        entities.remove(data)
    except ValueError:
        pass


class Animate(_Visible):

    def __init__(self, resource_id, position):
        self.resource_id = resource_id
        self.position = position


@dataclass
class MoveToTarget:
    screen_source: Vector
    target: Vector
    resource_id: typing.Any
    time: float
    position: Vector = None
    layer: float = 200
    special_draw_func: typing.Any = None
    next_time: float = 0.0
    idx: int = 0
    loop: bool = False
    end_cb: typing.Any = None
    angle = 0  # degrees
    flip_x = False
    flip_y = False
    scale = 1  # 0.0 < zoom in 0.1 steps
    alpha = 1  # 0.0 <= alpha <= 1.0



class AnimateOnce(_Visible):
    loop = False

    def __init__(self, position: Vector, resource_id):
        self.resource_id = resource_id
        self.position = position
        self.end_cb = remove_after_animation
        self.cb_data = self


class _Trigger:

    def __init__(self, name, event_id):
        self.event_id = event_id
        self.name = name


class RectTrigger(_Trigger):
    def __init__(self, name, event_id, rect):
        super().__init__(name, event_id)
        self.rect = rect


logger.debug("imported")
