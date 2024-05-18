# -*- coding: utf-8 -*-
import logging

import pygame

from game.camera import Camera
from game.entities.fly_bounding_box import FlyBoundingBox
from game.eventing import EventDispatcher
from game.gamescene import GameScene
from game.graphicshandler import GraphicsHandler
from game.level_loader import LevelLoader
from game.level_progressor import LevelProgressor
from game.musichandler import MusicHandler
from game.pausescene import PauseScene
from game.resources import ResourceLoader
from game.settings import Settings
from game.soundhandler import SoundHandler
from game.transitions import FadeOutAndIn

logger = logging.getLogger(__name__)
logger.debug("importing...")


class Factory:
    _resource_loader = None
    _sound_handler = None
    _music_handler = None
    _graphics_handler = None
    _menu_font = None

    @staticmethod
    def create_camera():
        world_rect = Factory._create_world_rect()
        screen_rect = Factory._create_screen_rect(world_rect)
        return Camera(world_rect, screen_rect)

    @staticmethod
    def create_bounding_box():
        world_rect = Factory._create_world_rect()
        screen_rect = Factory._create_screen_rect(world_rect)
        return FlyBoundingBox(pygame.Rect(0, 0, screen_rect.w * Settings.bounding_box_w_factor,
                                          screen_rect.h * Settings.bounding_box_h_factor))

    @staticmethod
    def create_sound_handler():
        # singleton
        if not Factory._sound_handler:
            Factory._sound_handler = SoundHandler()
        return Factory._sound_handler

    @staticmethod
    def create_music_handler():
        # singleton
        if not Factory._music_handler:
            Factory._music_handler = MusicHandler()
        return Factory._music_handler

    @staticmethod
    def create_graphics_handler():
        # singleton
        if not Factory._graphics_handler:
            resource_loader = Factory.create_resource_loader()
            Factory._graphics_handler = GraphicsHandler(pygame.display, resource_loader)
        return Factory._graphics_handler

    @staticmethod
    def create_resource_loader():
        # singleton
        if not Factory._resource_loader:
            Factory._resource_loader = ResourceLoader()
        return Factory._resource_loader

    @staticmethod
    def create_level_progressor():
        return LevelProgressor(LevelLoader(), Factory.create_music_handler(), Factory)

    @staticmethod
    def create_game_scene(level):
        transition = Factory.create_transition()
        return GameScene(transition,
                         pygame.display,
                         pygame.event,
                         pygame.time.Clock(),
                         Factory.create_camera(),
                         Factory.create_bounding_box(),
                         level,
                         draw_clock=pygame.time.Clock(),
                         update_clock=pygame.time.Clock(),
                         event_dispatcher=Factory.create_event_dispatcher(),
                         sound_handler=Factory.create_sound_handler(),
                         music_handler=Factory.create_music_handler(),
                         graphics_handler=Factory.create_graphics_handler(),
                         factory=Factory)

    @staticmethod
    def create_menu_font():
        # singleton
        if not Factory._menu_font:
            Factory._menu_font = pygame.font.Font(None, 30)
        return Factory._menu_font

    @staticmethod
    def create_pause_scene():
        font = Factory.create_menu_font()
        return PauseScene(pygame.event, pygame.display, font, Factory.create_transition(),
                          Factory.create_music_handler())

    @staticmethod
    def create_event_dispatcher():
        return EventDispatcher()

    @staticmethod
    def create_transition():
        clock = pygame.time.Clock()
        return FadeOutAndIn(pygame.display, clock, Settings)

    @staticmethod
    def _create_screen_rect(world_rect):
        screen_rect = world_rect.copy()
        screen_rect.center = (Settings.resolution[0] / 2, Settings.resolution[1] / 2)
        return screen_rect

    @staticmethod
    def _create_world_rect():
        return pygame.Rect(0, 0, Settings.resolution[1], Settings.resolution[1])


logger.debug("imported")
