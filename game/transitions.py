# -*- coding: utf-8 -*-
#
# New BSD license
#
# Copyright (c) DR0ID
# This file 'transitions.py' is part of pw-35
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the <organization> nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL DR0ID BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""
The transitions.

.. versionchanged:: 0.0.0.0
    initial version

"""
from __future__ import print_function, division

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

# __all__ = []    # list of public visible parts of this module

import pygame

from game.scenemanager import Transition

logger = logging.getLogger(__name__)
logger.debug("importing...")


class FadeOutAndIn(Transition):

    def __init__(self, screen_provider, clock, settings, duration_in_s=0.5):
        self.settings = settings
        self.total_duration_in_s = duration_in_s
        self.screen_provider = screen_provider
        self.clock = clock

    def run(self, from_scene=None, to_scene=None):
        logging.info("trans %s -> %s", from_scene, to_scene)
        # fadeout
        duration_ms = self.total_duration_in_s * 1000 / 2
        screen = self.screen_provider.get_surface()
        fader = screen.copy()
        fader.fill((255, 255, 255))
        dt = 0
        t = 0
        self.clock.tick(self.settings.draw_fps)  # update clock so dt later is correct!
        while t < duration_ms:
            screen.fill((0, 0, 0))
            fraction = t / duration_ms
            value = int(255 * (1 - fraction) + 0 * fraction)
            fader.fill((value, value, value))
            if from_scene:
                from_scene.draw(screen, do_flip=False)
            screen.blit(fader, (0, 0), None, pygame.BLEND_RGB_MULT)
            t += dt
            dt = self.clock.tick(self.settings.draw_fps)
            pygame.display.flip()
        dt = 0
        t = 0
        while t < duration_ms and to_scene:
            screen.fill((0, 0, 0))
            fraction = t / duration_ms
            value = int(0 * (1 - fraction) + 255 * fraction)
            fader.fill((value, value, value))
            if to_scene:
                to_scene.draw(screen, do_flip=False)
            screen.blit(fader, (0, 0), None, pygame.BLEND_RGB_MULT)
            t += dt
            dt = self.clock.tick(self.settings.draw_fps)
            pygame.display.flip()


logger.debug("imported")
