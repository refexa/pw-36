# -*- coding: utf-8 -*-
import logging

from game.entities.entities import Ship
from game.gui import Gauge, ShieldGauge

logger = logging.getLogger(__name__)
logger.debug("importing...")


class Level:

    def __init__(self):
        self.guide = None
        self.portals = []
        self.triggers = []
        self.walls = []
        self.enemies = []
        self.powerups = []
        self.mines = []
        self.ship: Ship = None
        self.shield_gauge: ShieldGauge = None
        self.dark_matter_gauge: Gauge = None
        self.groups = {}
        self.size = (0, 0)


logger.debug("imported")
