# -*- coding: utf-8 -*-
#
# New BSD license
#
# Copyright (c) DR0ID
# This file 'scenemanager.py' is part of pw-35
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
The scene manager and its related classes.

.. versionchanged:: 0.0.0.0
    initial version

"""
from __future__ import print_function, division

import abc
import collections
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

__all__ = ["SceneManager", "Scene", "Transition"]  # list of public visible parts of this module

logger = logging.getLogger(__name__)
logger.debug("importing...")


class Transition(metaclass=abc.ABCMeta):

    def run(self, from_scene=None, to_scene=None):
        raise NotImplementedError


class SceneManager:
    class PopCmd:
        def __init__(self, count=1, transition=None):
            self._transition = transition
            self._count = count

        def execute(self, scene_manager):
            scene_manager.pop(self._count, transition=self._transition)

    class PushCmd:
        def __init__(self, scene, transition=None):
            self._transition = transition
            self._scene = scene

        def execute(self, scene_manager):
            scene_manager.push(self._scene, transition=self._transition)

    class PushMultipleCmd:
        def __init__(self, scenes, transition=None):
            self._transition = transition
            self._scenes = scenes

        def execute(self, scene_manager):
            scene_manager.push(self._scenes, transition=self._transition)

    class ExchangeCmd:
        def __init__(self, scene, transition=None):
            self._transition = transition
            self._scene = scene

        def execute(self, scene_manager):
            scene_manager.exchange(self._scene, transition=self._transition)

    class NoneCmd:
        def execute(self, scene_manager):
            return

    def __init__(self):
        self._stack = []
        self._current = None

    def update(self, cmd=None):
        if cmd:
            cmd.execute(self)
        return self._current

    def pop(self, count=1, transition: Transition = None):
        n = 0
        while self._stack:
            n += 1
            exited_scene = self._stack.pop()
            if n == 1 and transition:
                to_scene = None
                if self._stack:
                    to_scene = self._stack[-count] if count <= len(self._stack) else None
                transition.run(exited_scene, to_scene)
            exited_scene.exit()
            self._current = None
            if self._stack:
                self._current = self._stack[-1]
                self._current.resume()
            if n >= count:
                break
        # if self._stack:
        #     self._current = self._stack[-1]
        # else:
        #     self._current = None
        return self._current

    def push(self, scene, transition=None):
        if not isinstance(scene, collections.abc.Sequence):
            scene = [scene]
        for idx, s in enumerate(scene):
            if self._current:
                self._current.pause()
            self._stack.append(s)
            s.enter()
            if idx == 0 and transition:
                transition.run(self._current, scene[-1])
            self._current = s

    def exchange(self, scene, transition=None):
        if self._stack:
            exited_scene = self._stack.pop()
            exited_scene.exit()
        self._stack.append(scene)
        scene.enter()
        if transition:
            transition.run(self._current, scene)
        self._current = scene

    def top(self):
        self._current = self._stack[-1]
        return self._current


class Scene(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def enter(self):
        pass

    @abc.abstractmethod
    def exit(self):
        pass

    @abc.abstractmethod
    def pause(self):
        pass

    @abc.abstractmethod
    def resume(self):
        pass

    @abc.abstractmethod
    def run(self):
        raise NotImplementedError

    @abc.abstractmethod
    def draw(self, screen, fill_color=(0, 0, 0), do_flip=True):
        raise NotImplementedError


logger.debug("imported")
