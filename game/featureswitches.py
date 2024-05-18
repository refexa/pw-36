# -*- coding: utf-8 -*-
import logging
from collections import deque

import pygame
from pygame import KEYDOWN

logger = logging.getLogger(__name__)
logger.debug("importing...")


class Features:
    _key_seq = deque(maxlen=2)

    debug_draw_on_11 = False  # 11
    fps_info_on_12 = True  # 12
    guide_move_13 = True  # 13
    wall_collision_color_on_14 = False  # 14
    move_ship_with_cam_15 = False  # 15
    collisions_on_16 = True  # 16
    collisions_ship_wall_on_17 = True  # 17
    collisions_ship_bounding_box_on_18 = True  # 18
    collisions_bullets_19 = True  # 19
    log_bullet_lifecycle_20 = False
    mouse_steering_on_21 = False
    collisions_ship_enemy_22 = True
    mouse_steering2_on_23 = True
    log_on_collision_24 = False
    debug_fill_color_on_25 = False
    collisions_ship_wall_on_26 = True
    normal_draw_on_27 = True
    enemy_start_fire_when_active_28 = True
    move_dark_matter_on_29 = True
    disable_updates_on_30 = False
    cam_shake_on_31 = True
    star_field_32 = True

    @staticmethod
    def handle_events(events):
        for e in events:
            if e.type == KEYDOWN:
                if e.key in (pygame.K_0,
                             pygame.K_1,
                             pygame.K_2,
                             pygame.K_3,
                             pygame.K_4,
                             pygame.K_5,
                             pygame.K_6,
                             pygame.K_7,
                             pygame.K_8,
                             pygame.K_9,
                             ):
                    Features._key_seq.append(e.key)
                    key = tuple(Features._key_seq)
                    if key == (pygame.K_1, pygame.K_1,):
                        Features.debug_draw_on_11 = not Features.debug_draw_on_11
                        logger.info(f"Features.debug_draw_on_11: {Features.debug_draw_on_11}")
                    elif key == (pygame.K_1, pygame.K_2,):
                        Features.fps_info_on_12 = not Features.fps_info_on_12
                        logger.info(f"Features.fps_info_on_12: {Features.fps_info_on_12}")
                    elif key == (pygame.K_1, pygame.K_3,):
                        Features.guide_move_13 = not Features.guide_move_13
                        logger.info(f"Features.guide_move_13: {Features.guide_move_13}")
                    elif key == (pygame.K_1, pygame.K_4,):
                        Features.wall_collision_color_on_14 = not Features.wall_collision_color_on_14
                        logger.info(f"Features.wall_collision_color_on_14: {Features.wall_collision_color_on_14}")
                    elif key == (pygame.K_1, pygame.K_5,):
                        Features.move_ship_with_cam_15 = not Features.move_ship_with_cam_15
                        logger.info(f"Features.move_ship_with_cam_15: {Features.move_ship_with_cam_15}")
                    elif key == (pygame.K_1, pygame.K_6,):
                        Features.collisions_on_16 = not Features.collisions_on_16
                        logger.info(f"Features.collisions_on_16: {Features.collisions_on_16}")
                    elif key == (pygame.K_1, pygame.K_7,):
                        Features.collisions_ship_wall_on_17 = not Features.collisions_ship_wall_on_17
                        logger.info(f"Features.collisions_ship_wall_on_17: {Features.collisions_ship_wall_on_17}")
                    elif key == (pygame.K_1, pygame.K_8,):
                        Features.collisions_ship_bounding_box_on_18 = not Features.collisions_ship_bounding_box_on_18
                        logger.info(
                            f"Features.collisions_ship_bounding_box_on_18: "
                            f"{Features.collisions_ship_bounding_box_on_18}")
                    elif key == (pygame.K_1, pygame.K_9,):
                        Features.collisions_bullets_19 = not Features.collisions_bullets_19
                        logger.info(f"Features.collisions_bullets_19: {Features.collisions_bullets_19}")
                    elif key == (pygame.K_2, pygame.K_0,):
                        Features.log_bullet_lifecycle_20 = not Features.log_bullet_lifecycle_20
                        logger.info(f"Features.log_bullet_lifecycle_20: {Features.log_bullet_lifecycle_20}")
                    elif key == (pygame.K_2, pygame.K_1,):
                        Features.mouse_steering_on_21 = not Features.mouse_steering_on_21
                        logger.info(f"Features.mouse_steering_on_21: {Features.mouse_steering_on_21}")
                    elif key == (pygame.K_2, pygame.K_2,):
                        Features.collisions_ship_enemy_22 = not Features.collisions_ship_enemy_22
                        logger.info(f"Features.collisions_ship_enemy_22: {Features.collisions_ship_enemy_22}")
                    elif key == (pygame.K_2, pygame.K_3,):
                        Features.mouse_steering2_on_23 = not Features.mouse_steering2_on_23
                        logger.info(f"Features.mouse_steering2_on_23: {Features.mouse_steering2_on_23}")
                    elif key == (pygame.K_2, pygame.K_4,):
                        Features.log_on_collision_24 = not Features.log_on_collision_24
                        logger.info(f"Features.log_on_collision_24: {Features.log_on_collision_24}")
                    elif key == (pygame.K_2, pygame.K_5,):
                        Features.debug_fill_color_on_25 = not Features.debug_fill_color_on_25
                        logger.info(f"Features.debug_fill_color_on_25: {Features.debug_fill_color_on_25}")
                    elif key == (pygame.K_2, pygame.K_6,):
                        Features.collisions_ship_wall_on_26 = not Features.collisions_ship_wall_on_26
                        logger.info(f"Features.collisions_ship_wall_on_26: {Features.collisions_ship_wall_on_26}")
                    elif key == (pygame.K_2, pygame.K_7,):
                        Features.normal_draw_on_27 = not Features.normal_draw_on_27
                        logger.info(f"Features.normal_draw_on_27: {Features.normal_draw_on_27}")
                    elif key == (pygame.K_2, pygame.K_8,):
                        Features.enemy_start_fire_when_active_28 = not Features.enemy_start_fire_when_active_28
                        logger.info(
                            f"Features.enemy_start_fire_when_active_28: {Features.enemy_start_fire_when_active_28}")
                    elif key == (pygame.K_2, pygame.K_9,):
                        Features.move_dark_matter_on_29 = not Features.move_dark_matter_on_29
                        logger.info(
                            f"Features.move_dark_matter_on_29: {Features.move_dark_matter_on_29}")
                    elif key == (pygame.K_3, pygame.K_0,):
                        Features.disable_updates_on_30 = not Features.disable_updates_on_30
                        logger.info(
                            f"Features.disable_updates_on_30: {Features.disable_updates_on_30}")
                    elif key == (pygame.K_3, pygame.K_1,):
                        Features.cam_shake_on_31 = not Features.cam_shake_on_31
                        logger.info(
                            f"Features.cam_shake_on_31: {Features.cam_shake_on_31}")
                    elif key == (pygame.K_3, pygame.K_2,):
                        Features.star_field_32 = not Features.star_field_32
                        logger.info(
                            f"Features.star_field_32: {Features.star_field_32}")

                    if len(key) == 2:
                        Features._key_seq.clear()
                elif e.scancode == 53:  # '§'
                    logger.info("reset features queue!")
                    Features._key_seq.clear()


logger.debug("imported")
