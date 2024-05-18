# -*- coding: utf-8 -*-
import logging

logger = logging.getLogger(__name__)
logger.debug("importing...")


class FlyBoundingBox:

    def __init__(self, rect):
        self.rect = rect


logger.debug("imported")
