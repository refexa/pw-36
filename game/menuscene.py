# -*- coding: utf-8 -*-
import logging

import pygame

from game.featureswitches import Features
from game.musichandler import MusicHandler
from game.resourcegame import res_id_sound_fire_1
from game.scenemanager import Scene, SceneManager
from game.settings import Mixer, Settings
from game.soundhandler import SoundHandler

logger = logging.getLogger(__name__)
logger.debug("importing...")


class MenuScene(Scene):

    def __init__(self, event_provider, screen_provider, font, transition, music_handler: MusicHandler, factory,
                 sound_handler: SoundHandler):
        self.event_provider = event_provider
        self._screen_provider = screen_provider
        self.text: str = ("{0}\n"
                          "~~~~~~~~~~~~~~~~~~\n\n\n"
                          "Get to the other portal but watch your dark matter reserves (top) and shields.\n"
                          "Dark matter is what drives your ship.\n"
                          "Shields need it, cannons too.\n"
                          "Refill it with the blue, but avoid the red."
                          "\n\n\n~~~\n\n\n"
                          "Music volume: [K](- {1:1} +)[I]\n"
                          "Sound volume: [L](- {2:1} +)[O]\n"
                          "Show starfield [S]: {4}\n"
                          "Controls [M]: {3}"
                          "\n\n\n~~~\n\n\n"
                          "[Q] to quit.\n\n"
                          "[Space] to start.")
        self.font: pygame.font.Font = font
        self._transition = transition
        self._music_handler = music_handler
        self._sound_handler = sound_handler
        self._factory = factory
        self._volume_step = 0.1

    def enter(self):
        pygame.display.set_caption(f"{Settings.caption}")

    def exit(self):
        pygame.event.clear()

    def pause(self):
        pygame.event.clear()

    def resume(self):
        pygame.display.set_caption(f"{Settings.caption}")

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
                return SceneManager.PopCmd(2, self._transition)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    return SceneManager.PopCmd(2, self._transition)
                    return SceneManager.PopCmd(2, self._transition)
                elif event.key == pygame.K_SPACE:
                    return SceneManager.PushCmd(self._factory.create_level_progressor(), self._transition)
                elif event.key == pygame.K_i:
                    v = self._music_handler.get_volume() + self._volume_step
                    self._music_handler.set_volume(v)
                elif event.key == pygame.K_k:
                    v = self._music_handler.get_volume() - self._volume_step
                    self._music_handler.set_volume(v)
                elif event.key == pygame.K_o:
                    v = self._sound_handler.get_volume() + self._volume_step
                    self._sound_handler.set_volume(v)
                    self._sound_handler.play(res_id_sound_fire_1)
                elif event.key == pygame.K_l:
                    v = self._sound_handler.get_volume() - self._volume_step
                    self._sound_handler.set_volume(v)
                    self._sound_handler.play(res_id_sound_fire_1)
                elif event.key == pygame.K_m:
                    Features.mouse_steering2_on_23 = not Features.mouse_steering2_on_23
                elif event.key == pygame.K_s:
                    Features.star_field_32 = not Features.star_field_32
            elif event.type == Mixer.ENDEVENT_SONG:
                self._music_handler.on_end_event()

    def draw(self, screen, fill_color=(0, 0, 0), do_flip=True):
        music_volume = round(self._music_handler.get_volume(), 1)
        sound_volume = round(self._sound_handler.get_volume(), 1)
        # mouse_on = "🖱 mouse\n\nControl the ship with the mouse. Use left button to fire." if Features.mouse_steering2_on_23 else "⌨ keyboard\n Control the ship with the '←','→','↑','↓' keys or 'a','s','d','w', fire pressing 'space'"
        mouse_text = "mouse\n\nControl the ship with the mouse. Use left button to fire."
        keyboard_text = "Keyboard\n\nControl the ship with the [arrow] keys or [A],[S],[D],[W], fire pressing [SPACE]"
        mouse_on = mouse_text if Features.mouse_steering2_on_23 else keyboard_text
        text = str.format(self.text, Settings.caption, music_volume, sound_volume, mouse_on, Features.star_field_32)
        lines = text.split('\n')
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
