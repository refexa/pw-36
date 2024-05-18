# -*- coding: utf-8 -*-
"""pygame_boilerplate.py - boilerplate for a simple game prototype"""

import logging

import pygame

import game.resourcegame
from game import scenemanager, settings
from game.factories import Factory
from game.menuscene import MenuScene
from game.settings import Settings
from game.textscene import TextScene

logger = logging.getLogger(__name__)

logger.debug("importing...")


class Game(object):

    def run(self):
        """run loop"""
        resource_loader = Factory.create_resource_loader()
        resource_loader.configure_loaders(game.resourcegame.loaders)

        sound_resources = resource_loader.load(game.resourcegame.resource_config_sound)
        music_resources = resource_loader.load(game.resourcegame.resource_config_music)

        sound_handler = Factory.create_sound_handler()
        sound_handler.initialize(sound_resources)

        music_handler = Factory.create_music_handler()
        music_handler.initialize(music_resources)
        music_handler.set_end_event_type(settings.Mixer.ENDEVENT_SONG)
        music_handler.play(music_resources.keys(), 1000, True)

        graphics_handler = Factory.create_graphics_handler()
        graphics_handler.initialize()
        graphics_handler.load_resources(game.resourcegame.resource_config_image)

        stack = scenemanager.SceneManager()

        font = Factory.create_menu_font()
        credits_text = ("Credits\n\n\n\n\n"
                        "*\ngummbumm\nPyNon\ntabishrfx\nDR0ID\n*\n\n\n\n\n"
                        "pyweek36\n2023\n\n\n\n\n\n\n"
                        "Thanks for playing.\n\n\n\n\n"
                        "...press any key to quit...")
        credits_scene = TextScene(pygame.event, pygame.display, credits_text, font, Factory.create_transition(),
                                  music_handler, lambda: music_handler.stop(500))
        stack.push(credits_scene)

        end_scene = TextScene(pygame.event, pygame.display, "End", font, Factory.create_transition(), music_handler)
        stack.push(end_scene)

        if Settings.skip_menu:
            stack.push(Factory.create_level_progressor())
        else:
            menu_scene = MenuScene(pygame.event, pygame.display, font,
                                   Factory.create_transition(), music_handler, Factory, sound_handler)
            stack.push(menu_scene)

        scene = stack.top()

        # main loop
        while scene:
            cmd = scene.run()
            if cmd:
                scene = stack.update(cmd)


def main():
    pygame.mixer.pre_init(settings.Mixer.frequency, buffer=settings.Mixer.buffer_size)
    pygame.init()
    Game().run()


if __name__ == '__main__':
    main()

logger.debug("imported")
