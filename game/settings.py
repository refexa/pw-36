# -*- coding: utf-8 -*-
from __future__ import print_function
from dataclasses import dataclass
import os

import logging

import pygame

logger = logging.getLogger(__name__)
logger.debug("importing...")


@dataclass
class Settings:
    resolution = 1024, 768
    caption = "Dark matter keeper"
    draw_fps = 60
    ups = 120
    skip_menu = False
    initial_level = 1
    levels = [
        "resources/map/dev_1.json",
        "resources/map/map_1.json",
        "resources/map/map_2.json",
        "resources/map/map_3.json",
        "resources/map/map_4.json",
        "resources/map/map_5.json",
        "resources/map/map_6.json",
        "resources/map/map_7.json",
    ]
    ship_speed_x_forward = 150 * 1.6
    ship_speed_x_backwards = 90 * 1.6
    ship_speed_y = 150 * 1.6
    guide_speed = 90

    bounding_box_w_factor = 0.75
    bounding_box_h_factor = 0.9

    draw_dt_s = 0  # will be set according to draw_fps, just here for auto-completion

    ship_enemy_collision_trauma = 0.3
    ship_hit_trauma = 0.08
    ship_wall_trauma = 0.09


@dataclass
class Mixer:
    frequency = 0  # mixer.pre_init()
    buffer_size = 128  # mixer.pre_init()
    num_channels = 32  # mixer.set_num_channels()
    # reserved_channels = 9   # mixer.set_reserved()
    file_dir = os.path.join('resources', 'audio')

    # channel reservations
    player_shoot = 0  # ch = mixer.Channel(id); ch.play(sound, ...)
    player_explode = 1
    easy_enemy_shoot = 2
    easy_enemy_explode = 3
    medium_enemy_shoot = 4
    medium_enemy_explode = 5
    hard_enemy_shoot = 6
    hard_enemy_explode = 7
    ambient = 8

    ENDEVENT_SONG = pygame.USEREVENT + 100
    ENDEVENT_SOUND = pygame.USEREVENT + 101


try:
    # define a _custom.py file to override some settings (useful while developing)
    # noinspection PyUnresolvedReferences,PyProtectedMember
    from game._custom import Settings as CustomSettings

    logger.debug("Custom settings found...")
    for k, v in CustomSettings.__dict__.items():
        if str(k).startswith("__"):
            continue
        if not hasattr(Settings, k):
            logger.warning("Custom setting found but is not in Settings: %s=%s", k, v)
        setattr(Settings, k, v)
        logger.debug("Overwriting Settings.%s=%s", k, v)
except ImportError:
    pass

Settings.draw_dt_s = 1.0 / Settings.draw_fps

logger.debug("imported")
