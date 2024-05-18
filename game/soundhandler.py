# -*- coding: utf-8 -*-
import logging
from dataclasses import dataclass
from typing import Any

import pygame

from game import settings
from game.resourcespygame import SoundResource, SoundResourceDescription

logger = logging.getLogger(__name__)
logger.debug("importing...")


class SoundHandler:
    @dataclass
    class _SoundConfig:
        resource_id: Any
        """the loaded pygame.mixer.Sound object"""
        sound: pygame.mixer.Sound
        """the filename loaded"""
        filename: str
        """any free channel if None, otherwise use reserved channel"""
        channel_id: int = -1
        """predefined volume from resource loading to level out different sound volumes"""
        volume: float = 1.0
        """replace other sound that is playing, otherwise do not play (use a force flag if channel_id is None)"""
        replace: bool = True

    def __init__(self):
        self._sound_map = {}  # {resource_id : _SoundConfig}
        self._master_volume = 0.5

    def initialize(self, resources):
        """
        Initialize the mixer.
        :type resources: the resources map, {resource_id: resource}
        :return: None
        """
        # filter for SoundResources!
        # put the resources into self._sound_map
        channel_ids = set()
        for resource_id, res in resources.items():
            if isinstance(res, SoundResource):
                rd: SoundResourceDescription = res.resource_description
                conf = self._SoundConfig(resource_id, res.sound, rd.filename, res.channel_id, res.volume,
                                         res.replace)
                conf.channel_id = -1 if conf.channel_id is None else conf.channel_id
                channel_ids.add(res.channel_id)
                self._sound_map[resource_id] = conf
                logger.debug(f'SoundHandler.initialize: Added {resource_id}:{rd.filename}')
            else:
                logger.info(f'SoundHandler.initialize: Skipped {resource_id}:{res}')

        channel_ids.discard(None)
        num_reserved_channels = len(channel_ids)
        # assert settings.Mixer.reserved_channels == num_reserved_channels, "configured and settings channels differ!"

        # # re-initialize
        # pygame.mixer.quit()
        # pygame.mixer.init(fequency=settings.Mixer.frequency, buffer=settings.Mixer.buffer_size)

        # set num channels and reserved channels
        pygame.mixer.set_num_channels(settings.Mixer.num_channels)
        actual_reserved = pygame.mixer.set_reserved(num_reserved_channels)
        if actual_reserved < num_reserved_channels:
            logger.warning("Could not reserve %s channels, only got %s", num_reserved_channels, actual_reserved)

    def play(self, resource_id):
        """
        Play sound. On the configured channel, otherwise just on a free channel.
        :param resource_id: resource to play.
        :return:
        """
        # logger.debug(f'SoundHandler.play: {self._sound_map}')
        res = self._sound_map.get(resource_id, None)
        # if res is None:
        #     logger.error("Sound resource_id not loaded: %s", resource_id)
        #     return
        sound = res.sound
        sound.set_volume(res.volume * self._master_volume)
        if res.channel_id >= 0:  # channel id 0 might be special here!
            # reserved channels
            channel = pygame.mixer.Channel(res.channel_id)
            if not channel.get_busy() or res.replace:
                channel.play(sound)
        else:
            channel = pygame.mixer.find_channel(res.replace)
            if channel:
                channel.play(sound)
            else:
                logger.debug("SoundHandler: did not find any free channel!")

    def stop(self, fade_ms=0):
        """
        Stop playing the sounds.
        :param fade_ms: fade the volume out in ms.
        :return: None
        """
        for i in range(settings.Mixer.num_channels):
            ch = pygame.mixer.Channel(i)
            ch.fadeout(fade_ms)

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

    def get_volume(self):
        return self._master_volume

    def set_end_event_type(self, end_event_type):
        """
        Set the end event type to be fired when the sound ends. Set to None to stop firing it.
        :param end_event_type: the event type to fire.
        :return: None
        """
        pass

    def on_end_event(self):
        """
        Called when the end_event is registered in the event loop.
        :return:
        """
        # not sure what this should do
        pass

    def update(self):
        pass


logger.debug("imported")
