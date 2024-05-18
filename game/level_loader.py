# -*- coding: utf-8 -*-
import logging
import math

import pygame
from pygame.math import Vector3 as Vector

from game import pytmxloader
from game.behavior import Group, EasyBehavior, MediumBehavior, HardBehavior
from game.gui import Gauge, ShieldGauge
from game.entities.entities import Ship, RectTrigger, Wall, EnemyEasy, EnemyMedium, EnemyHard, \
    PowerUp, Mine, Cannon, Portal
from game.entities.guide import Guide
from game.gamescene import evt_id_end_reached
from game.level import Level
from game.pytmxloader import OBJECT_LAYER_TYPE, ObjectLayerInfo
from game.resourcegame import res_id_portal_start, res_id_portal_end
from game.settings import Settings

logger = logging.getLogger(__name__)
logger.debug("importing...")


class LevelLoader:

    def __init__(self):
        self.image_cache = {}  # {key: image}

    def load_level(self, file_path) -> Level:
        level = Level()
        map_info = pytmxloader.load_map_from_file_path(file_path)
        tw = map_info.properties["tilewidth"]
        th = map_info.properties["tileheight"]
        h = map_info.properties["height"]
        w = map_info.properties["width"]
        size = tw * w, th * h
        level.size = size
        groups = {}
        for idx, layer in enumerate(map_info.layers):
            if not layer.visible:
                continue
            if layer.layer_type == OBJECT_LAYER_TYPE:
                self._load_object_layer(idx, layer, level, groups)
            # elif layer.layer_type == TILE_LAYER_TYPE:
            #     self._load_tile_layer(idx, self.image_cache, layer, scheduler, self.sprites, self.entities, obj_types)
            else:
                logger.warning("layer type '%s' not processed", layer.layer_type)
        level.groups = groups
        return level

    @staticmethod
    def _load_object_layer(idx, layer: ObjectLayerInfo, level: Level, groups):
        guide_line = []
        start_position = None
        end_position = None
        group_idx = -min(groups.keys()) if groups else 1
        for obj in layer.objects:
            kind = obj.type

            rect = pygame.Rect(obj.pixel_rect)
            pos = Vector(rect.centerx, rect.centery, 0)
            radius = math.hypot(rect.w, rect.h) / 2
            group_idx += 1

            logger.info("load obj of type '%s' pos: %s radius: %s", kind, pos, radius)
            if kind == "guide":
                xy = Vector(obj.x, obj.y, 0)
                for idx, p1 in enumerate(obj.points):
                    s = xy + Vector(*p1, 0)
                    guide_line.append(s)
            elif kind == "Start":
                start_position = Vector(*rect.center, 0)
                level.guide = Guide(start_position.copy(), Vector(Settings.guide_speed, 0, 0))
                level.portals.append(Portal(start_position.copy(), radius, 0, res_id_portal_start))  # start portal
                pass
            elif kind == "End":
                end_position = pos.copy()
                level.triggers.append(RectTrigger("end", evt_id_end_reached, rect))
                level.portals.append(Portal(Vector(*rect.center, 0), radius, 0, res_id_portal_end))  # end portal
                pass
            elif kind == "Player":
                cannons = [Cannon(Vector(1, 0, 0)),
                           Cannon(Vector(-1, 0, 0)),
                           Cannon(Vector(0, 1, 0)),
                           Cannon(Vector(0, -1, 0))]
                level.ship = Ship(cannons, pos, radius)
                level.shield_gauge = ShieldGauge((level.ship.rect.w, 9), 20, 20, 0)
                level.dark_matter_gauge = Gauge((200, 18), 20, 20, 0)
                level.shield_gauge.dark_matter_gauge = level.dark_matter_gauge  # I know it's dirty! I don't care!
                pass
            elif kind == "Wall":
                xy = Vector(obj.x, obj.y, 0)
                for idx, p1 in enumerate(obj.points[:-1]):
                    p2 = obj.points[idx + 1]
                    s = xy + Vector(*p1, 0)
                    e = xy + Vector(*p2, 0)
                    if bool(obj.properties.get("invert", False)):
                        s, e = e, s

                    diff = e - s
                    normal = diff.rotate(90, Vector(0, 0, 1)).normalize()
                    half_width = 5  # todo should the come from Tiled too?
                    p1 = s + normal * half_width
                    p2 = e + normal * half_width
                    p3 = e - normal * half_width
                    p4 = s - normal * half_width
                    points = [p1, p2, p3, p4]
                    wall = Wall(s, e, points)
                    level.walls.append(wall)
                pass
            elif kind == "EnemyEasy":
                g_id = int(obj.properties.get("groupId", -group_idx))

                cannons = [Cannon(Vector(-1, 0, 0))]
                enemy = EnemyEasy(cannons, pos, radius, g_id)
                for c in enemy.cannons:
                    c.interval = 1.0

                group = groups.setdefault(g_id, Group([], EasyBehavior))
                group.entities.append(enemy)
                level.enemies.append(enemy)
                pass
            elif kind == "EnemyMedium":
                g_id = int(obj.properties.get("groupId", -group_idx))

                cannons = [Cannon(Vector(-1, 0, 0)), Cannon(Vector(1, 0, 0))]
                enemy = EnemyMedium(cannons, pos, radius, g_id)
                for c in enemy.cannons:
                    c.interval = 1.5

                group = groups.setdefault(g_id, Group([], MediumBehavior))
                group.entities.append(enemy)
                level.enemies.append(enemy)
                pass
            elif kind == "EnemyHard":
                g_id = int(obj.properties.get("groupId", -group_idx))

                cannons = [Cannon(Vector(-1, 0, 0)),
                           Cannon(Vector(1, 0, 0)),
                           Cannon(Vector(0, 1, 0)),
                           Cannon(Vector(0, -1, 0))]
                enemy = EnemyHard(cannons, pos, radius, g_id)
                for c in enemy.cannons:
                    c.interval = 0.2

                group = groups.setdefault(g_id, Group([], HardBehavior))
                group.entities.append(enemy)
                level.enemies.append(enemy)
                pass
            elif kind == "BKB":
                power_up = PowerUp(pos, radius)
                level.powerups.append(power_up)
                pass
            elif kind == "RKB":
                mine = Mine(pos, radius)
                level.mines.append(mine)
                pass
            else:
                logger.error("unknown object type '%s' in object layer '%s'", kind, layer.name)

        if level.guide:
            if not guide_line:
                guide_line = [start_position.copy(), end_position.copy()]
            level.guide.track = guide_line


logger.debug("imported")
