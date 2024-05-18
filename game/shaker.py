# -*- coding: utf-8 -*-
#
# New BSD license
#
# Copyright (c) DR0ID
# This file 'Shaker.py' is part of pw-33
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
Shaker implementation.

"""
from __future__ import print_function

import logging

__version__ = '1.0.0.0'

# for easy comparison as in sys.version_info but digits only
__version_info__ = tuple([int(d) for d in __version__.split('.')])

__author__ = "DR0ID"
__email__ = "dr0iddr0id {at} gmail [dot] com"
__copyright__ = "DR0ID @ 2022"
__credits__ = ["DR0ID"]  # list of contributors
__maintainer__ = "DR0ID"
__license__ = "New BSD license"

import random

from pygame.math import Vector3 as Vector

logger = logging.getLogger(__name__)
logger.debug("importing...")


def rand_range(a, b):
    return random.random() * (b - a) + a


class Shaker(object):
    """
    Based on: https://kidscancode.org/godot_recipes/2d/screen_shake/
    """

    def __init__(self):
        self.decay = 0.8  # How quickly the shaking stops [0, 1].
        self.max_offset = Vector(75, 100, 0)  # Maximum hor/ver shake in pixels.
        self.max_roll = 0.1  # Maximum rotation in radians (use sparingly).
        self.trauma = 0.0  # Current shake strength.
        self.trauma_power = 2  # Trauma exponent. Use [2, 3].

    def add_trauma(self, amount):
        self.trauma = min(self.trauma + amount, 1.0)

    def update(self, delta):
        # if self.target:
        # global_position = get_node(target).global_position
        offset = Vector(0, 0, 0)

        if self.trauma:
            self.trauma = max(self.trauma - self.decay * delta, 0)
            self.shake(offset)
        return offset

    def shake(self, offset):
        amount = pow(self.trauma, self.trauma_power)
        # rotation = self.max_roll * amount * rand_range(-1, 1)
        offset.x = self.max_offset.x * amount * rand_range(-1, 1)
        offset.y = self.max_offset.y * amount * rand_range(-1, 1)
        return offset


logger.debug("imported")
