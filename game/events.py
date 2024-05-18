# -*- coding: utf-8 -*-
import logging as _logging

from game.resourcegame import next_id as _next_id

_logger = _logging.getLogger(__name__)
_logger.debug("importing...")

evt_id_end_reached = _next_id()
evt_id_ship_wall_collision = _next_id()
evt_id_bullet_wall_collision = _next_id()
evt_id_ship_enemy_collision = _next_id()
evt_id_bullet_enemy_collision = _next_id()
evt_id_bullet_ship_collision = _next_id()
evt_id_ship_powerup_collision = _next_id()
evt_id_ship_mine_collision = _next_id()

evt_id_died = _next_id()  # signature: evt_id, reason, position

_logger.debug("imported")
