# -*- coding: utf-8 -*-
from __future__ import print_function

import logging

__version__ = '1.0.0.0'

# for easy comparison as in sys.version_info but digits only
__version_info__ = tuple([int(d) for d in __version__.split('.')])

__author__ = "DR0ID"
__email__ = "dr0iddr0id {at} gmail [dot] com"
__copyright__ = "DR0ID @ 2023"
__credits__ = ["DR0ID"]  # list of contributors
__maintainer__ = "DR0ID"
__license__ = "New BSD license"

import pygame

from game.musichandler import MusicHandler
from game.scenemanager import Scene, SceneManager
from game.settings import Mixer

# __all__ = []  # list of public visible parts of this module

logger = logging.getLogger(__name__)
logger.debug("importing...")


class PauseScene(Scene):

    def __init__(self, event_provider, screen_provider, font, transition, music_handler: MusicHandler,
                 on_exit=None):
        self._on_exit = on_exit
        self.event_provider = event_provider
        self._screen_provider = screen_provider
        self.text: str = "Paused\n\n\n\n [Q] to quit to main menu.\n\n[R] or [ESC] to resume the game."
        self.font: pygame.font.Font = font
        self._transition = transition
        self._music_handler = music_handler

    def enter(self):
        pass

    def exit(self):
        pygame.event.clear()
        if self._on_exit:
            self._on_exit()

    def pause(self):
        pygame.event.clear()

    def resume(self):
        pass

    def run(self):
        self.draw(self._screen_provider.get_surface())  # draw initially
        cmd = self.update(0)
        while not cmd:
            cmd = self.update(0)
            self.draw(self._screen_provider.get_surface())
        return cmd

    def update(self, dt_s):
        # for event in [self.event_provider.wait()]:
        for event in [self.event_provider.wait()]:
            if event.type == pygame.QUIT:
                return SceneManager.PopCmd(5, self._transition)
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_r, pygame.K_ESCAPE):
                    # resume
                    return SceneManager.PopCmd(1, self._transition)
                elif event.key == pygame.K_q:
                    return SceneManager.PopCmd(3, self._transition)
            elif event.type == Mixer.ENDEVENT_SONG:
                self._music_handler.on_end_event()

    def draw(self, screen, fill_color=(0, 0, 0), do_flip=True):
        lines = self.text.split('\n')
        labels = []
        total_height = 0
        for line in lines:
            label = self.font.render(line, True, (255, 255, 255), (0, 0, 0))
            labels.append(label)
            h = label.get_size()[1]
            total_height += h
        screen_rect = self._screen_provider.get_surface().get_rect()
        y = screen_rect.centery - total_height / 2
        if fill_color:
            screen.fill(fill_color)

        for label in labels:
            r = label.get_rect(midtop=(screen_rect.centerx, y))
            screen.blit(label, r)
            y += r.h

        if do_flip:
            self._screen_provider.flip()


logger.debug("imported")
