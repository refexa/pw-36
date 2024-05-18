# -*- coding: utf-8 -*-
import logging

logger = logging.getLogger(__name__)
logger.debug("importing...")


class Guide:
    def __init__(self, position, velocity):
        self.velocity = velocity
        self.position = position
        self.track = None
        self.current_track_idx = 0
        self.direction = velocity.normalize()


logger.debug("imported")
