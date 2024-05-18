# -*- coding: utf-8 -*-
import logging

import pygame

from game import settings
from game.resourcespygame import MusicResource

logger = logging.getLogger(__name__)
logger.debug("importing...")


class MusicHandler:
    """
    NB: Be sure to set the end event type with MusicHandler.set_end_event_type(). There are two ways to process the
    music queue:
    1. In the game's update() routine, call MusicHandler.update() before any event handling. The MusicHandler peeks for
       the end event type. If the game's event handler clears the event queue, MusicHandler will never see the event.
    2. Or, in your event handler, handle the end event type by calling MusicHandler.on_end_event().
    """

    def __init__(self):
        self.music_resources = {}
        self.music_queue = []
        self.i_playing = 0
        self.fade_ms = 0
        self.loop = True
        self._master_volume = 0.5

    def initialize(self, resources):
        """
        Initialize the music.
        :type resources: the resources map, {resource_id: resource}
        :return: None
        """
        # process only of type MusicResource
        logger.debug(f'MusicHandler: resources {resources}')
        for res_id, res in resources.items():
            logger.debug(f'MusicHandler: resource {{{res_id}: {res}}}')
            if isinstance(res, MusicResource):
                self.music_resources[res_id] = res
                logger.debug(f'MusicHandler: added {res.resource_description.filename}')
            else:
                logger.debug(f'MusicHandler: skipped {type(res)}')

    def play(self, resource_ids: list, fade_ms: int = 0, loop: bool = True):
        """
        Play the music. If more than one is passed then it should play them one after another.
        :param resource_ids: the ids to play.
        :param fade_ms: fade the volume in. Time in ms.
        :param loop: if true the entire list of songs should be looped.
        :return: None
        """
        del self.music_queue[:]
        self.i_playing = 0
        self.fade_ms = 0 if fade_ms is None else fade_ms
        self.loop = loop
        for res_id in resource_ids:
            assert res_id in self.music_resources
            self.music_queue.append(self.music_resources[res_id])
        if self.i_playing < len(self.music_queue):
            song = self.music_queue[self.i_playing]
            pygame.mixer.music.load(song.resource_description.filename)
            pygame.mixer.music.play(0, 0, self.fade_ms)

    def stop(self, fade_ms=None):
        """
        Stop playing the song.
        :param fade_ms: fade the volume out in ms; if None, use the instance default fade_ms.
        :return: None
        """
        if fade_ms is None:
            fade_ms = self.fade_ms
        pygame.mixer.music.fadeout(fade_ms)

    def set_volume(self, volume: float):
        """
        Set the volume.
        :param volume: volume in range 0.0 to 1.0 (inclusive).
        :return: None
        """
        # clamp to 0.0 - 1.0 (inclusive) range
        volume = volume if volume <= 1.0 else 1.0
        volume = volume if volume >= 0.0 else 0.0
        self._master_volume = volume
        if pygame.mixer.music.get_busy():
            now_playing = self.music_queue[self.i_playing]
            song_volume = now_playing.resource_description.volume
            pygame.mixer.music.set_volume(song_volume * self._master_volume)

    def get_volume(self):
        return self._master_volume

    def set_end_event_type(self, end_event_type=settings.Mixer.ENDEVENT_SONG):
        """
        Set the end event type to be fired when the music ends. Set to None to stop firing it.
        :param end_event_type: the event type to fire.
        :return: None
        """
        pygame.mixer.music.set_endevent(end_event_type)

    def on_end_event(self):
        """
        Called when the end_event is registered in the event loop.
        :return:
        """
        # this should probably queue the next music.
        logger.debug('MusicHandler.on_end_event fired')
        self.i_playing += 1
        if self.i_playing >= len(self.music_queue):
            self.i_playing = 0
            if not self.loop:
                return
        song = self.music_queue[self.i_playing]
        pygame.mixer.music.load(song.resource_description.filename)
        pygame.mixer.music.play(0, 0, self.fade_ms)

    def update(self):
        if pygame.event.peek(settings.Mixer.ENDEVENT_SONG):
            self.on_end_event()


logger.debug("imported")
