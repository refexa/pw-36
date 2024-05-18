# -*- coding: utf-8 -*-
import logging

import pygame.display

from game.level import Level
from game.level_loader import LevelLoader
from game.musichandler import MusicHandler
from game.scenemanager import Scene, SceneManager
from game.settings import Settings

logger = logging.getLogger(__name__)
logger.debug("importing...")


class LevelProgressor(Scene):

    def __init__(self, level_loader, music_handler: MusicHandler, factory):
        self.factory = factory
        self.music_handler = music_handler
        self._level_loader: LevelLoader = level_loader
        self.current_level_idx = Settings.initial_level
        self.current_level_name = Settings.levels[self.current_level_idx]
        self._current_level: Level = None
        self.game_scene = None

    def next(self):
        self.current_level_idx += 1
        if self.current_level_idx == len(Settings.levels):
            self.current_level_name = None
        else:
            self.current_level_name = Settings.levels[self.current_level_idx]
        self._current_level = None

    def get_current_level(self):
        if not self._current_level and self.current_level_name:
            logger.info("LevelProgressor: load level idx %s: %s", self.current_level_idx, self.current_level_name)
            self._current_level = self._level_loader.load_level(self.current_level_name)
        return self._current_level

    def enter(self):
        self._current_level = None
        self.current_level_idx = Settings.initial_level
        logger.info("LevelProgressor: enter, reset level idx to %s", self.current_level_idx)

    def exit(self):
        pass

    def pause(self):
        pass

    def resume(self):
        if self.game_scene and self.game_scene.end_condition:
            self.next()
            logger.info("LevelProgressor: resume, progressing to level idx %s", self.current_level_idx)
        else:
            self._current_level = None
            logger.info("LevelProgressor: retry level idx %s", self.current_level_idx)

    def run(self):
        self.music_handler.update()  # call this before handle events

        level = self.get_current_level()
        if level:
            pygame.display.set_caption(f"{Settings.caption} - {self.current_level_idx}")
            self.game_scene = self.factory.create_game_scene(level)
            transition = self.factory.create_transition()
            return SceneManager.PushCmd(self.game_scene, transition)
        else:
            pygame.display.set_caption(f"{Settings.caption}")
            # game has finished
            return SceneManager.PopCmd(2, self.factory.create_transition())
            # font = pygame.font.Font(None, 30)
            # return SceneManager.ExchangeCmd(TextScene(pygame.event, pygame.display, "End", font, self.factory.create_transition()))

    def draw(self, screen, fill_color=(0, 0, 0), do_flip=True):
        pass



logger.debug("imported")
