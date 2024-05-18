# -*- coding: utf-8 -*-
from __future__ import print_function

import itertools
import logging
import math
import random

import pygame
from pygame.math import Vector3 as Vector

from game import tweening
from game.behavior import Group
from game.camera import Camera
from game.entities.entities import Animate, EBulletTemplate, EnemyEasy, EnemyHard, EnemyMedium, Ship, TimerData, Bullet, \
    FBulletTemplate, \
    Wall, SpecialDraw, EHardBulletTemplate, EMediumBulletTemplate, MoveToTarget, AnimateOnce
from game.eventing import EventDispatcher
from game.events import *
from game.featureswitches import Features
from game.graphicshandler import GraphicsHandler
from game.level import Level
from game.musichandler import MusicHandler
from game.resourcegame import res_id_portal_start, res_id_portal_end, res_id_pointer, res_id_sound_fire_3, \
    res_id_sound_fire_1, res_id_sound_fire_4, res_id_sound_fire_6, res_id_sound_hit, res_id_sound_no_bullet, \
    res_id_powerup, res_id_ship_explode, res_id_sound_start_level, res_id_sound_ship_explode, \
    res_id_bullet_ship_explosion, res_id_bullet_enemy_explosion, res_id_ship_wall_sparks, res_id_bullet_wall_hit, \
    res_id_sound_enemy_explode
from game.scenemanager import Scene, SceneManager
from game.settings import Settings
from game.shaker import Shaker
from game.soundhandler import SoundHandler
from game.tweening import Tweener

logger = logging.getLogger(__name__)
logger.debug("importing...")


class GameScene(Scene):
    x_axis = Vector(1, 0, 0)

    def __init__(self, transition, screen_provider, event_provider, clock: pygame.time.Clock, camera, bounding_box,
                 level: Level, draw_clock, update_clock, event_dispatcher: EventDispatcher, sound_handler: SoundHandler,
                 music_handler: MusicHandler, graphics_handler: GraphicsHandler, factory):
        self.factory = factory
        self._graphics_handler = graphics_handler
        self._music_handler = music_handler
        self._sound_handler = sound_handler
        self._event_dispatcher = event_dispatcher
        self._draw_clock = draw_clock
        self._update_clock = update_clock
        self._level = level
        self._event_provider = event_provider
        self._screen_provider = screen_provider
        self._clock = clock
        self._transition = transition
        self._camera: Camera = camera
        self._bounding_box = bounding_box
        self._timers = []
        self._bullets = []
        self.end_condition = None
        self._game_time = 0
        self._contacts = []
        self._draw_list = []
        self._moves = []
        self._cmd = None
        self._gauges_draw_entity = None
        self._pointer = None
        self._pointer_line = None
        self._active_enemies = []
        self._is_level_initialized = False
        self._tweener = Tweener(logger_instance=False)  # disable logging
        self._shaker = Shaker()
        self._stars = {}

    def enter(self):
        pygame.event.clear()
        self.init_level()
        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)
        self._cmd = None

    def exit(self):
        pygame.event.clear()
        pygame.mouse.set_visible(True)
        pygame.event.set_grab(False)

    def pause(self):
        pygame.event.clear()
        pygame.mouse.set_visible(True)
        pygame.event.set_grab(False)

    def resume(self):
        pygame.event.clear()
        self.init_level()
        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)
        self._cmd = None

    def init_level(self):
        if self._is_level_initialized:
            return
        self._is_level_initialized = True

        self._camera.look_at(self._level.guide.position)
        timer = TimerData(self._log_fps_info, 1, 0)
        if not any((t for t in self._timers if t.func == timer.func)):
            self._timers.append(timer)

        # self._timers.append(self._level.ship.cannon.timer)
        for e in self._level.enemies:
            # for cannon in e.cannons:
            #     cannon.interval = 1.0
            if not Features.enemy_start_fire_when_active_28:
                self._ship_fire(e)

        self._event_dispatcher.set_handler(evt_id_end_reached, self._on_win)
        self._event_dispatcher.set_handler(evt_id_ship_wall_collision, self._on_ship_wall_collision)
        self._event_dispatcher.set_handler(evt_id_ship_enemy_collision, self._on_ship_enemy_collision)
        self._event_dispatcher.set_handler(evt_id_bullet_ship_collision, self._on_bullet_ship_collision)
        self._event_dispatcher.set_handler(evt_id_bullet_enemy_collision, self._on_bullet_enemy_collision)
        self._event_dispatcher.set_handler(evt_id_ship_powerup_collision, self._on_ship_powerup_collision)
        self._event_dispatcher.set_handler(evt_id_ship_mine_collision, self._on_ship_mine_collision)
        self._event_dispatcher.set_handler(evt_id_bullet_wall_collision, self._on_bullet_wall_collision)
        self._event_dispatcher.set_handler(evt_id_died, self._on_die)

        Wall.special_draw_func = self._draw_wall

        self._draw_list = list(
            itertools.chain(self._level.enemies, self._level.powerups, self._level.mines, self._bullets,
                            self._level.portals, self._level.walls))
        self._draw_list.append(self._level.ship)
        self._gauges_draw_entity = SpecialDraw(self._draw_gauges, layer=101)
        self._draw_list.append(self._gauges_draw_entity)
        self._draw_list.append(SpecialDraw(self._draw_star_field, layer=-1))

        self._stars = {}
        r = pygame.Rect((0, 0), self._level.size)
        r.midleft = tuple(self._level.ship.position.xy)
        r.inflate_ip(800, 200)
        for layer in range(5):
            for count in range(100):
                pos = Vector(random.randrange(r.left, r.right), random.randrange(r.top, r.bottom), 0)
                self._stars.setdefault(layer, []).append(pos)

        pygame.mouse.set_pos((Settings.resolution[0] / 2, Settings.resolution[1] / 2))
        self._pointer = Animate(res_id_pointer, self._camera.to_world(pygame.mouse.get_pos()))
        self._pointer.layer = Ship.layer - 1
        self._pointer_line = SpecialDraw(self._draw_pointer_line, layer=self._pointer.layer - 1)
        if Features.mouse_steering2_on_23:
            self._draw_list.append(self._pointer)
            self._draw_list.append(self._pointer_line)
        self._tweener.create_tween_by_end(self._level.ship, "alpha", 0.0, 1.0, 1)
        self._sound_handler.play(res_id_sound_start_level)

    def _on_win(self, evt_id, trig, *args):
        logger.error(">>>>>> WIN! WIN! WIN! WIN! <<<<<<")
        if self.end_condition is not True:
            # self._level.triggers.remove(trig)
            # todo setup win things: sound, visualize ship vanish, timer, etc
            self._draw_list.remove(self._gauges_draw_entity)
            self._hide_pointer()
            self._timers.clear()
            duration = 3
            self._timers.append(TimerData(self._set_pop1_cmd, duration, -1))
            self.end_condition = True
            self._tweener.create_tween_by_end(self._level.ship, "alpha", 1.0, 0, duration,
                                              ease_function=tweening.ease_in_quad)

    def _hide_pointer(self):
        if Features.mouse_steering2_on_23:
            try:
                self._draw_list.remove(self._pointer)
                self._draw_list.remove(self._pointer_line)
            except ValueError:
                pass

    def _on_die(self, evt_id, reason, position, *args):
        logger.error(">>>>>> LOOSE! LOOSE! <<<<<<: %s", reason)
        if self.end_condition is not False:
            # todo setup loose things: sound, ship explosion, timer, etc.
            self._draw_list.remove(self._gauges_draw_entity)
            self._hide_pointer()
            self._timers.clear()
            self._timers.append(TimerData(self._set_pop1_cmd, 3, -1))
            self.end_condition = False
            self._level.ship.direction.update(0, 0, 0)
            self._draw_list.remove(self._level.ship)
            explosion = AnimateOnce(self._level.ship.position.copy(), res_id_ship_explode)
            explosion.angle = random.randint(0, 360)
            explosion.next_time = self._game_time
            explosion.layer = 900
            self._draw_list.append(explosion)
            self._sound_handler.play(res_id_sound_ship_explode)

    # def _check_end_condition(self):
    #     if self._end_condition is not None:
    #         if self._end_condition:
    #             # return cmd for next level
    #             pass
    #         else:
    #             # retry this level
    #             pass
    #
    #     return None

    def _on_bullet_ship_collision(self, evt_id, bullet, ship, point, touching, *args):
        if Features.log_on_collision_24:
            logger.error("!!! ship hits bullet at %s !!!", point)
        self._remove_bullet(bullet)
        if touching is False:
            self._sound_handler.play(res_id_sound_hit)
            explosion = AnimateOnce(point, res_id_bullet_ship_explosion)
            explosion.layer = 900
            explosion.angle = random.randint(0, 360)
            self._draw_list.append(explosion)
            if self._level.shield_gauge.current <= 0:
                self._event_dispatcher.dispatch_event(evt_id_died, "Hit without shields", ship.position)
            self._level.shield_gauge.decrease(1)
            if Features.cam_shake_on_31:
                self._shaker.add_trauma(Settings.ship_hit_trauma)

    def _on_bullet_enemy_collision(self, evt_id, bullet, enemy, point, touching, *args):
        if Features.log_on_collision_24:
            logger.error("!!! bullet hits enemy at %s !!!", point)
        self._remove_bullet(bullet)
        self._remove_enemy(enemy)
        if touching is False:
            # self._sound_handler.play(res_id_sound_hit)
            self._sound_handler.play(res_id_sound_enemy_explode)
            explosion = AnimateOnce(point, res_id_bullet_enemy_explosion)
            explosion.layer = 900
            explosion.angle = random.randint(0, 360)
            self._draw_list.append(explosion)

    def _on_ship_wall_collision(self, evt_id, ship, wall, point, touching, direction, *args):
        if Features.log_on_collision_24:
            logger.error("!!! ship hits wall at %s !!! repeated touching: %s", point, touching)
        if touching is False:
            self._sound_handler.play(res_id_sound_hit)
            explosion = AnimateOnce(point, res_id_ship_wall_sparks)
            explosion.angle = random.randint(0, 360)
            self._draw_list.append(explosion)
            self._level.shield_gauge.decrease(5)
            if self._level.shield_gauge.current <= 0:  # not forgiving
                self._event_dispatcher.dispatch_event(evt_id_died, "Collided with wall, shields too weak!",
                                                      ship.position)
            if Features.cam_shake_on_31:
                self._shaker.add_trauma(Settings.ship_wall_trauma)

        ship.position += direction

    def _on_bullet_wall_collision(self, evt_id, b, w, point, touching, *args):
        if Features.log_on_collision_24:
            logger.error("!!! bullet hits wall at %s !!! repeated touching: %s", point, touching)
        if touching is False:
            self._remove_bullet(b)
            self._sound_handler.play(res_id_sound_hit)  # todo different sound?
            explosion = AnimateOnce(point, res_id_bullet_wall_hit)
            explosion.angle = random.randint(0, 360)
            self._draw_list.append(explosion)

    def _on_ship_enemy_collision(self, evt_id, ship, enemy, point, touching, *args):
        if Features.log_on_collision_24:
            logger.error("!!! ship hits enemy at %s !!!", point)
        if touching is False:
            explosion = AnimateOnce(point, res_id_ship_wall_sparks)
            explosion.angle = random.randint(0, 360)
            self._draw_list.append(explosion)
            self._level.shield_gauge.decrease(2)
            if self._level.shield_gauge.current <= 0:
                self._event_dispatcher.dispatch_event(evt_id_died, "Collided with other ship, shields too weak!",
                                                      ship.position)
            # destroy enemy
            self._sound_handler.play(res_id_sound_enemy_explode)
            self._remove_enemy(enemy)
            explosion = AnimateOnce(point, res_id_bullet_enemy_explosion)
            explosion.layer = 900
            explosion.angle = random.randint(0, 360)
            self._draw_list.append(explosion)
            if Features.cam_shake_on_31:
                self._shaker.add_trauma(Settings.ship_enemy_collision_trauma)

    def _on_ship_powerup_collision(self, evt_id, ship, powerup, point, touching, *args):
        if Features.log_on_collision_24:
            logger.error("!!! ship hits powerup at %s !!!", point)
        # self._sound_handler.play(res_id_sound_hit)
        self._remove_powerup(powerup)
        self._level.dark_matter_gauge.increase(powerup.amount)

    def _on_ship_mine_collision(self, evt_id, ship, mine, point, touching, *args):
        if Features.log_on_collision_24:
            logger.error("!!! ship hits mine at %s !!!", point)
        # self._sound_handler.play(res_id_sound_hit)
        self._remove_mine(mine)
        self._level.dark_matter_gauge.decrease(mine.amount)
        if self._level.dark_matter_gauge.current <= 0:
            self._event_dispatcher.dispatch_event(evt_id_died, "Run out of dark matter, the mine absorbed it all!",
                                                  ship.position)

    def _log_fps_info(self, timer_data: TimerData, *args):
        if Features.fps_info_on_12:
            fps = self._draw_clock.get_fps()
            ups = self._update_clock.get_fps()
            loops = self._clock.get_fps()
            logger.info("fps: %s  ups: %s  loops: %s  bullets: %s  draw_list: %s  contacts: %s",
                        fps if math.isinf(fps) else round(fps),
                        ups if math.isinf(ups) else round(ups),
                        loops if math.isinf(loops) else round(loops),
                        len(self._bullets),
                        len(self._draw_list),
                        len(self._contacts))
            logger.info(self._graphics_handler._get_transformed.cache_info()
                        )

    def run(self):
        screen = self._screen_provider.get_surface()
        self.draw(screen)  # draw initially

        draw_clock = self._draw_clock
        draw_dt = Settings.draw_dt_s
        real_time = 0
        self._game_time = 0

        up_clock = self._update_clock
        accumulator = 0
        fixed_dt_s = 1 / Settings.ups
        max_dt = 3 * fixed_dt_s
        next_frame_time = 0
        while not self._cmd:
            raw_dt_s = self._clock.tick() / 1000
            if raw_dt_s > max_dt:
                raw_dt_s = max_dt
            real_time += raw_dt_s
            accumulator += raw_dt_s
            while accumulator > fixed_dt_s:
                accumulator -= fixed_dt_s
                up_clock.tick()
                if not Features.disable_updates_on_30:
                    self._game_time += fixed_dt_s
                self.update(fixed_dt_s)
            if real_time >= next_frame_time:
                draw_clock.tick()
                next_frame_time += draw_dt
                self.draw(screen)
        return self._cmd

    def update(self, dt_s):
        self._music_handler.update()  # this must come before event handler; it peeks for ENDEVNET_SONG
        self.handle_events()

        if Features.disable_updates_on_30:
            return
        if self.end_condition:
            portal = [p for p in self._level.portals if p.resource_id == res_id_portal_end][0]
            delta = portal.position - self._level.ship.position
            if delta.length_squared() <= 1:
                self._level.ship.direction.update(0, 0, 0)
            else:
                self._level.ship.direction.update(delta)

            self._update_ship(dt_s)
            self._update_shield(dt_s)
            self._update_dark_matter(dt_s)
        elif self.end_condition is False:
            self._update_ship(dt_s)
        else:
            if Features.guide_move_13:
                self._update_guide(dt_s)
            self._camera.look_at(self._level.guide.position)
            self._bounding_box.rect.midleft = self._camera.world_rect.midleft

            self._update_ship(dt_s)
            self._update_enemies(dt_s)
            self._update_bullets(dt_s)
            self._check_triggers()
            self._check_collisions()
            self._update_shield(dt_s)
            self._update_dark_matter(dt_s)
            # if Features.move_dark_matter_on_29:
            #     self._update_moves(dt_s)

        # always process these
        if Features.cam_shake_on_31:
            offset = self._shaker.update(dt_s)
            self._camera.offset.update(offset)
        self._process_timers()
        self._tweener.update(dt_s)

    def _update_guide(self, dt_s):
        guide = self._level.guide
        # guide.position += guide.velocity * dt_s
        direction, idx = self._get_next_track_direction(guide.position, guide.current_track_idx, guide.track)
        guide.current_track_idx = idx
        if direction:
            guide.direction = direction
        guide.velocity = direction * Settings.guide_speed
        guide.position += guide.velocity * dt_s

    def _update_enemies(self, dt_s):
        # update active enemies, remove out of sight, add new in sight
        world_rect = self._camera.world_rect
        rect_collide_point = world_rect.collidepoint
        for enemy in reversed(self._level.enemies):
            if rect_collide_point(*enemy.position.xy):
                if enemy not in self._active_enemies:
                    self._active_enemies.append(enemy)
                    if Features.enemy_start_fire_when_active_28:
                        self._ship_fire(enemy)
            else:
                if (enemy.position - self._level.guide.position).dot(self._level.guide.direction) < 0:
                    self._remove_enemy(enemy)

        # activate group
        for g in (self._level.groups.get(g_id, None) for g_id in set((e.group_id for e in self._active_enemies))):
            if g:
                g.activate(self)

        # # update active
        # for enemy in self._active_enemies:
        #     enemy.position += enemy.velocity * dt_s

    # def _update_moves(self, dt_s):
    #     for m in reversed(self._moves):
    #         m.time -= dt_s
    #         target = m.target
    #         direction = target - self._camera.to_world(m.screen_source.xy)
    #         m.velocity = direction / m.time
    #         m.position += m.velocity * dt_s
    #         if (target - m.position).length_squared() < 1:
    #             self._remove_move_to_target(m)

    def _update_ship(self, dt_s):
        ship = self._level.ship
        if ship.direction:  # 0-vector check
            ship.direction.normalize_ip()
        speed_x = Settings.ship_speed_x_forward
        if ship.direction.x < 0:
            speed_x = Settings.ship_speed_x_backwards
        speed_y = Settings.ship_speed_y

        velocity = Vector(ship.direction.x * speed_x, ship.direction.y * speed_y, 0)
        if Features.move_ship_with_cam_15 and Features.guide_move_13:
            velocity += self._level.guide.velocity

        ship.position += velocity * dt_s
        ship.rect.center = ship.position.xy

    def _update_shield(self, dt_s):
        shield_gauge = self._level.shield_gauge
        transfer_amount = shield_gauge.update(dt_s)
        if transfer_amount and Features.move_dark_matter_on_29:
            screen_pos = Vector(*self._camera.screen_rect.midtop, 0)
            screen_pos.y += 10
            self._create_move_to_target(screen_pos, self._level.ship.position, res_id_powerup, 0.5)
        ship = self._level.ship
        shield_gauge.position.xy = ship.rect.move(-ship.rect.w // 2, -ship.rect.h // 2 - 10).center

    def _update_dark_matter(self, dt_s):
        dark_matter_gauge = self._level.dark_matter_gauge
        dark_matter_gauge.update(dt_s)

    def _update_bullets(self, dt_s):
        world_rect = self._camera.world_rect
        rect_collide_point = world_rect.collidepoint
        for b in reversed(self._bullets):
            b.position += b.velocity * dt_s
            if not rect_collide_point(*b.position.xy):
                self._remove_bullet(b)

    def _on_create_bullet(self, timer):
        ship, cannon = timer.data

        if ship == self._level.ship:
            dark_matter = self._level.dark_matter_gauge
            dark_matter.decrease(0.1)
            if dark_matter.current <= 0:
                # can't fire without dark matter
                self._sound_handler.play(res_id_sound_no_bullet)
                return

        # if heading should be relative to ship:
        # 1. define e1, e2 of ship, e.g. e1, e2 as an orthogonal base
        # 2. coord transform: heading_rel = e1 * hx + e2 * hy
        #     => heading_rel = ( (e1.x, e2.x) dot (x, y) , (e1.y, e2.y) dot (x, y) )

        if self._level.ship == ship:
            # use FBulletTemplate
            bullet = Bullet(FBulletTemplate(), ship.position.copy(), cannon.heading, ship)
            self._sound_handler.play(res_id_sound_fire_1)
        elif type(ship) == EnemyEasy:
            # use EBulletTemplate
            bullet = Bullet(EBulletTemplate, ship.position.copy(), cannon.heading, ship)
            self._sound_handler.play(res_id_sound_fire_3)
        elif type(ship) == EnemyMedium:
            # use EBulletTemplate
            bullet = Bullet(EMediumBulletTemplate, ship.position.copy(), cannon.heading, ship)
            self._sound_handler.play(res_id_sound_fire_4)
        elif type(ship) == EnemyHard:
            # use EBulletTemplate
            bullet = Bullet(EHardBulletTemplate, ship.position.copy(), cannon.heading, ship)
            self._sound_handler.play(res_id_sound_fire_6)
        else:
            # just in case...
            # use EBulletTemplate
            bullet = Bullet(EBulletTemplate, ship.position.copy(), cannon.heading, ship)
            self._sound_handler.play(res_id_sound_fire_3)
            logger.error("unknown ship type: %s", ship)

        angle = cannon.heading.angle_to(self.x_axis)
        if cannon.heading.y < 0:
            angle = 360 - angle

        bullet.angle = -angle
        self._bullets.append(bullet)
        self._draw_list.append(bullet)
        if Features.log_bullet_lifecycle_20:
            logger.debug("fire new bullet!")

    def _remove_bullet(self, bullet):
        try:
            self._bullets.remove(bullet)
            self._draw_list.remove(bullet)
            if Features.log_bullet_lifecycle_20:
                logger.debug("bullet removed at %s", bullet.position)
        except ValueError as ex:
            logger.error("Tried to remove bullet from list but was not present: %s", ex)

    def _remove_enemy(self, enemy):
        self._level.enemies.remove(enemy)
        self._draw_list.remove(enemy)
        self._ship_hold(enemy)
        try:
            self._active_enemies.remove(enemy)
        except ValueError:
            pass
        g: Group = self._level.groups.get(enemy.group_id, None)
        if g:
            try:
                g.entities.remove(enemy)
            except ValueError:
                pass
            if not g.entities:
                del self._level.groups[enemy.group_id]

    def _remove_powerup(self, powerup):
        try:
            self._level.powerups.remove(powerup)
            self._draw_list.remove(powerup)
            logger.debug("powerup removed at %s", powerup.position)
        except ValueError as ex:
            logger.error("Tried to remove powerup from list but was not present: %s", ex)

    def _remove_mine(self, mine):
        try:
            self._level.mines.remove(mine)
            self._draw_list.remove(mine)
            logger.debug("mine removed at %s", mine.position)
        except ValueError as ex:
            logger.error("Tried to remove powerup from list but was not present: %s", ex)

    def _create_move_to_target(self, screen_position, target, resource_id, time):
        m = MoveToTarget(screen_position, target, resource_id, time, position=self._camera.to_world(screen_position.xy))
        t = self._tweener.create_tween_by_end(m, "position", m.position, m.target, time, do_start=False, immediate=True,
                                              cb_end=self._remove_move_to_target, cb_args=[m], delta_update=True)
        p = t.parallel(
            self._tweener.create_tween_by_end(m, "alpha", 1.0, 0.05, time, ease_function=tweening.ease_in_quad,
                                              do_start=False, immediate=True, delta_update=True),
            self._tweener.create_tween_by_end(m, "scale", 1.0, 0.05, time, do_start=False, immediate=True,
                                              delta_update=True),
            self._tweener.create_tween_by_end(m, "angle", 0.0, 360, time, do_start=False, immediate=True,
                                              delta_update=True)
        )
        p.start()
        self._draw_list.append(m)
        self._moves.append(m)

    def _remove_move_to_target(self, move_to_target, *args):
        self._draw_list.remove(move_to_target)
        self._moves.remove(move_to_target)

    def _check_collisions(self):
        if not Features.collisions_on_16:
            return
        contacts = []
        if Features.collisions_ship_wall_on_17:
            self._check_ship_walls_collision(contacts)
        if Features.collisions_ship_bounding_box_on_18:
            # walls need to be checked before bounding box
            self._check_ship_bounding_box_collision(contacts)
        if Features.collisions_bullets_19:
            self._check_bullet_ship_enemy_collisions(contacts)
        if Features.collisions_ship_enemy_22:
            self._check_ship_enemy_collisions(contacts)
        self._check_ship_powerup_collisions(contacts)
        self._check_ship_mine_collisions(contacts)
        if Features.collisions_ship_wall_on_26:
            self._check_bullet_wall_collisions(contacts)
        self._contacts[:] = contacts

    def _check_ship_enemy_collisions(self, contacts):
        ship = self._level.ship
        ship_position_distance_squared_to = ship.position.distance_squared_to
        dispatch_event = self._event_dispatcher.dispatch_event
        for e in self._level.enemies:
            if ship_position_distance_squared_to(e.position) <= (ship.radius + e.radius) ** 2:
                # hit enemy
                contact = (ship, e)
                contacts.append(contact)
                dispatch_event(evt_id_ship_enemy_collision, ship, e, 0.5 * (ship.position + e.position),
                               contact in self._contacts)

    def _check_ship_powerup_collisions(self, contacts):
        ship = self._level.ship
        ship_position_distance_squared_to = ship.position.distance_squared_to
        dispatch_event = self._event_dispatcher.dispatch_event
        for p in self._level.powerups:
            if ship_position_distance_squared_to(p.position) <= (ship.radius + p.radius) ** 2:
                # hit enemy
                contact = (ship, p)
                contacts.append(contact)
                dispatch_event(evt_id_ship_powerup_collision, ship, p, 0.5 * (ship.position + p.position),
                               contact in self._contacts)

    def _check_ship_mine_collisions(self, contacts):
        ship = self._level.ship
        ship_position_distance_squared_to = ship.position.distance_squared_to
        dispatch_event = self._event_dispatcher.dispatch_event
        for p in self._level.mines:
            if ship_position_distance_squared_to(p.position) <= (ship.radius + p.radius) ** 2:
                # hit enemy
                contact = (ship, p)
                contacts.append(contact)
                dispatch_event(evt_id_ship_mine_collision, ship, p, 0.5 * (ship.position + p.position),
                               contact in self._contacts)

    def _check_bullet_wall_collisions(self, contacts):
        for b in self._bullets:
            b_rect = pygame.Rect(b.position.xy, (2 * b.radius, 2 * b.radius))
            colliders = b_rect.collideobjectsall(self._level.walls)
            for w in colliders:
                start_point = w.start_point
                end_point = w.end_point
                wall_direction = w.direction
                ship_radius = b.radius
                if not self._is_point_in_strip(start_point - 2 * ship_radius * wall_direction,
                                               end_point + 2 * ship_radius * wall_direction, b.position):
                    continue
                if self._is_point_in_strip(start_point, end_point, b.position):
                    # in 'between' the points
                    # check distance
                    wall_diff = end_point - start_point
                    projected: Vector = start_point + (b.position - start_point).dot(
                        wall_diff) / wall_diff.dot(wall_diff) * wall_diff
                    perpendicular = b.position - projected  # point away from wall
                    if perpendicular.length() < ship_radius:
                        # hit
                        contact = (b, w)
                        contacts.append(contact)
                        self._event_dispatcher.dispatch_event(evt_id_bullet_wall_collision, b, w, projected,
                                                              contact in self._contacts)
                        break

                else:
                    # check distances to points
                    if start_point.distance_to(b.position) < ship_radius:
                        # hit
                        contact = (b, w)
                        contacts.append(contact)
                        self._event_dispatcher.dispatch_event(evt_id_bullet_wall_collision, b, w, start_point,
                                                              contact in self._contacts)
                        break

                    if end_point.distance_to(b.position) < ship_radius:
                        # hit
                        contact = (b, w)
                        contacts.append(contact)
                        self._event_dispatcher.dispatch_event(evt_id_bullet_wall_collision, b, w, end_point,
                                                              contact in self._contacts)
                        break

    def _check_bullet_ship_enemy_collisions(self, contacts):
        ship = self._level.ship
        dispatch_event = self._event_dispatcher.dispatch_event
        for b in self._bullets:
            b_position_distance_squared_to = b.position.distance_squared_to
            if b.source == ship:
                for e in self._level.enemies:
                    if b_position_distance_squared_to(e.position) <= (b.radius + e.radius) ** 2:
                        # hit enemy
                        contact = (b, e)
                        contacts.append(contact)
                        dispatch_event(evt_id_bullet_enemy_collision, b, e, 0.5 * (b.position + e.position),
                                       contact in self._contacts)
                        break  # bullet can only hit one target therefore break enemies loop
            else:
                if b_position_distance_squared_to(ship.position) <= (b.radius + ship.radius) ** 2:
                    # hit ship
                    contact = (b, ship)
                    contacts.append(contact)
                    dispatch_event(evt_id_bullet_ship_collision, b, ship, 0.5 * (b.position + ship.position),
                                   contact in self._contacts)

    def _check_ship_walls_collision(self, contacts):
        # broad phase
        ship = self._level.ship
        colliders = ship.rect.collideobjectsall(self._level.walls)
        for wall in colliders:
            # narrow phase
            # a wall consists of 4 sides
            for idx, p1 in enumerate(wall.points):
                p0 = wall.points[idx - 1]

                start_point = p0  # wall.start_point
                end_point = p1  # wall.end_point
                wall_diff = end_point - start_point
                wall_direction = wall_diff.normalize()

                if Features.wall_collision_color_on_14:
                    screen = self._screen_provider.get_surface()
                    pygame.draw.line(screen, "red", self._camera.to_screen(start_point).xy,
                                     self._camera.to_screen(end_point).xy, 10)

                ship_radius = ship.radius
                if not self._is_point_in_strip(start_point - 2 * ship_radius * wall_direction,
                                               end_point + 2 * ship_radius * wall_direction, ship.position):
                    continue

                if self._is_point_in_strip(start_point, end_point, ship.position):
                    # in 'between' the points
                    # check distance
                    projected: Vector = start_point + (ship.position - start_point).dot(
                        wall_diff) / wall_diff.dot(wall_diff) * wall_diff
                    perpendicular = ship.position - projected  # point away from wall
                    if (dist := perpendicular.length()) < ship_radius:
                        # hit
                        depth = ship.radius - dist
                        perpendicular.scale_to_length(depth)
                        contact = (ship, wall)
                        contacts.append(contact)
                        self._event_dispatcher.dispatch_event(evt_id_ship_wall_collision, ship, wall, projected,
                                                              contact in self._contacts, perpendicular)

                        if Features.wall_collision_color_on_14:
                            pygame.draw.line(screen, "yellow", self._camera.to_screen(start_point).xy,
                                             self._camera.to_screen(end_point).xy, 6)
                            pygame.draw.circle(screen, "orange", self._camera.to_screen(projected).xy, 7)

                else:
                    # check distances to points
                    if (dist := start_point.distance_to(ship.position)) < ship_radius:
                        # hit
                        contact = (ship, wall)
                        contacts.append(contact)
                        direction = ship.position - start_point
                        direction.scale_to_length(ship_radius - dist)
                        self._event_dispatcher.dispatch_event(evt_id_ship_wall_collision, ship, wall, start_point,
                                                              contact in self._contacts, direction)
                        if Features.wall_collision_color_on_14:
                            pygame.draw.line(screen, "blue", self._camera.to_screen(start_point).xy,
                                             self._camera.to_screen(end_point).xy, 6)
                            pygame.draw.circle(screen, "orange", self._camera.to_screen(start_point).xy, 7)
                        continue

                    if (dist := end_point.distance_to(ship.position)) < ship_radius:
                        # hit
                        contact = (ship, wall)
                        contacts.append(contact)
                        direction = ship.position - end_point
                        direction.scale_to_length(ship_radius - dist)
                        self._event_dispatcher.dispatch_event(evt_id_ship_wall_collision, ship, wall, end_point,
                                                              contact in self._contacts, direction)
                        if Features.wall_collision_color_on_14:
                            pygame.draw.line(screen, "violet", self._camera.to_screen(start_point).xy,
                                             self._camera.to_screen(end_point).xy, 6)
                            pygame.draw.circle(screen, "orange", self._camera.to_screen(end_point).xy, 7)
                        continue

        if Features.wall_collision_color_on_14:
            self._screen_provider.flip()

    # __INLINE__
    def _is_point_in_strip(self, seg_p1, seg_p2, p):
        # https://math.stackexchange.com/a/701630
        d0 = seg_p2 - seg_p1
        len_d0 = d0.length()
        v = d0 / len_d0
        d1 = p - seg_p1
        r = v * d1
        return 0 <= r <= len_d0

    def _check_ship_bounding_box_collision(self, contacts):
        ship = self._level.ship
        if (ship_left := ship.position.x - ship.radius) < self._bounding_box.rect.left:
            delta = self._bounding_box.rect.left - ship_left
            ship.position += Vector(delta, 0, 0)
            # check for wall contacts to detect squash
            h = [c for c in contacts if type(c[0]) == Ship and type(c[1]) == Wall]
            if h and len(set((id(w[1]) for w in h))) >= 2:
                self._event_dispatcher.dispatch_event(evt_id_died, "Squashed to stardust!", ship.position)
        if (ship_right := ship.position.x + ship.radius) > self._bounding_box.rect.right:
            delta = ship_right - self._bounding_box.rect.right
            ship.position -= Vector(delta, 0, 0)
        if (ship_top := ship.position.y - ship.radius) < self._bounding_box.rect.top:
            delta = self._bounding_box.rect.top - ship_top
            ship.position += Vector(0, delta, 0)
        if (ship_bottom := ship.position.y + ship.radius) > self._bounding_box.rect.bottom:
            delta = ship_bottom - self._bounding_box.rect.bottom
            ship.position -= Vector(0, delta, 0)

        ship.rect.center = ship.position.xy

    def _check_triggers(self):
        colliders = self._level.ship.rect.collideobjectsall(self._level.triggers)
        for trig in reversed(colliders):
            self._event_dispatcher.dispatch_event(trig.event_id, trig)

    def _process_timers(self):
        now = self._game_time  # pygame.time.get_ticks() / 1000  # convert to seconds
        for timer in reversed(self._timers):
            if timer.next_time < 0:
                timer.next_time = now + timer.interval
                continue
            if timer.next_time <= now:
                func = timer.func()
                if func:
                    func(timer)
                    if timer.next_time <= 0:
                        timer.next_time = now
                    timer.next_time += timer.interval
                if not func or timer.interval == 0:
                    self._timers.remove(timer)

    def start_timer(self, func, interval, immediately=False, data=None):
        timer = TimerData(func, interval, 0 if immediately else -1, data)
        self._timers.append(timer)
        return timer.id

    def stop_timer(self, timer_id):
        for t in self._timers:
            if t.id == timer_id:
                self._timers.remove(t)
                break

    def handle_events(self):
        events = self._event_provider.get()
        Features.handle_events(events)  # toggle feature switches
        for event in events:
            # for event in [self._event_provider.wait()]:
            if event.type == pygame.QUIT:
                self._cmd = SceneManager.PopCmd(4, self._transition)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self._cmd = SceneManager.PushCmd(self.factory.create_pause_scene(), self._transition)
                elif event.key == pygame.K_SPACE:
                    self._ship_fire(self._level.ship)
                elif event.key == pygame.K_r:
                    # restart level
                    self.end_condition = False
                    self._set_pop1_cmd()
                elif event.key == pygame.K_k:
                    # restart level
                    self.end_condition = True
                    self._set_pop1_cmd()
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    self._ship_hold(self._level.ship)
            else:
                if Features.mouse_steering2_on_23:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        self._ship_fire(self._level.ship)
                    elif event.type == pygame.MOUSEBUTTONUP:
                        self._ship_hold(self._level.ship)
            # elif event.type == Mixer.ENDEVENT_SONG:
            #     self._music_handler.on_end_event()

        if self.end_condition is not None:
            return

        pressed = pygame.key.get_pressed()
        left = pressed[pygame.K_LEFT] or pressed[pygame.K_a]
        right = pressed[pygame.K_RIGHT] or pressed[pygame.K_d]
        up = pressed[pygame.K_UP] or pressed[pygame.K_w]
        down = pressed[pygame.K_DOWN] or pressed[pygame.K_s]
        self._level.ship.direction.update(right - left, down - up, 0)
        if Features.mouse_steering2_on_23:
            mx, my = pygame.mouse.get_pos()
            mouse_pos = self._camera.to_world((mx, my))
            self._pointer.position.update(mouse_pos)
            delta = mouse_pos - self._level.ship.position
            if delta.length_squared() <= 4:
                self._level.ship.direction.update(0, 0, 0)
            else:
                self._level.ship.direction.update(delta)

        if Features.mouse_steering_on_21:
            mx, my = pygame.mouse.get_pos()
            self._level.ship.direction.update(mx - Settings.resolution[0] / 2, my - Settings.resolution[1] / 2, 0)

    def _set_pop1_cmd(self, *args):
        self._cmd = SceneManager.PopCmd(1, self._transition)

    def _ship_fire(self, ship):
        for cannon in ship.cannons:
            if cannon.firing:
                continue
            cannon.firing = True
            cannon.timer_id = self.start_timer(self._on_create_bullet, cannon.interval, True, (ship, cannon))

    def _ship_hold(self, ship):
        for cannon in ship.cannons:
            self.stop_timer(cannon.timer_id)
            cannon.firing = False

    def draw(self, screen, fill_color=(0, 0, 0), do_flip=True):
        if Features.debug_fill_color_on_25:
            fill_color = (255, 0, 255)
        with self._camera.clip(screen):
            if fill_color:
                screen.fill(fill_color)

            # if Features.lerp_cam_on:
            #     self._cam.lerp(self.player.position, Settings.draw_dt_s)
            # else:
            #     self._cam.look_at(self.player.position.copy())
            if Features.debug_draw_on_11:
                self._draw_debug(screen)

            if Features.normal_draw_on_27:
                self._graphics_handler.draw(screen, self._camera, self._game_time, self._draw_list)

            if do_flip:
                self._screen_provider.flip()

    def _draw_pointer_line(self, screen, camera, g, res_map, *args):
        start = self._camera.to_screen(self._level.ship.position)
        end = self._camera.to_screen(self._pointer.position)
        pygame.draw.aaline(screen, "cornsilk", start, end, 1)

    def _draw_gauges(self, screen, camera, g, res_map):
        screen.blit(self._level.shield_gauge.image, self._camera.to_screen(self._level.shield_gauge.position).xy)

        image = self._level.dark_matter_gauge.image
        r = image.get_rect(midtop=self._camera.screen_rect.midtop)
        screen.blit(image, r.move(0, 10))

    def _draw_wall(self, screen, camera, wall, resource_map):
        points = [camera.to_screen(p).xy for p in wall.points]
        pygame.draw.polygon(screen, "goldenrod1", points)
        # pygame.draw.polygon(screen, "goldenrod", points, 2)
        pygame.draw.aalines(screen, "goldenrod", True, points, 1)

    star_colors = {
        0: "grey100",
        1: "grey80",
        2: "grey60",
        3: "grey40",
        4: "grey20",
    }

    def _draw_star_field(self, screen: pygame.Surface, camera, wall, resource_map):
        if not Features.star_field_32:
            return
        self__camera_to_screen = self._camera.to_screen
        screen_set_at = screen.set_at
        screen.lock()
        for layer, stars in self._stars.items():
            parallax = Vector(1.0 - layer / 5, 1.0, 1.0)
            color = self.star_colors.get(layer, "white")
            for star in stars:
                sp = self__camera_to_screen(star, parallax)
                screen_set_at(tuple(int(i) for i in sp.xy), color)
        screen.unlock()


    def _draw_debug(self, screen):
        origin = Vector(0, 0, 0)
        pygame.draw.circle(screen, "red", self._camera.to_screen(origin).xy, 5)
        pygame.draw.lines(screen, "snow2", False, [self._camera.to_screen(p).xy for p in self._level.guide.track])
        pygame.draw.circle(screen, "gray", self._camera.to_screen(self._level.guide.position).xy, 3)

        for w in self._level.walls:
            pygame.draw.line(screen, "red", self._camera.to_screen(w.start_point).xy,
                             self._camera.to_screen(w.end_point).xy)
            mid_point = (w.start_point + w.end_point) / 2
            pygame.draw.line(screen, "yellow", self._camera.to_screen(mid_point).xy,
                             self._camera.to_screen(mid_point + 20 * w.normal).xy)
            if Features.wall_collision_color_on_14:
                pygame.draw.rect(screen, "wheat2", self._camera.rect_to_screen(w.rect), 1)

        for p in self._level.portals:
            color = "green" if p.resource_id == res_id_portal_start else "brown"
            pygame.draw.circle(screen, color, self._camera.to_screen(p.position).xy, p.radius)

        for e in self._level.enemies:
            pygame.draw.circle(screen, "orange", self._camera.to_screen(e.position).xy, e.radius)

        for p in self._level.powerups:
            pygame.draw.circle(screen, "blue", self._camera.to_screen(p.position).xy, p.radius)

        for m in self._level.mines:
            pygame.draw.circle(screen, "red", self._camera.to_screen(m.position).xy, m.radius)

        for t in self._level.triggers:
            pygame.draw.rect(screen, "gray68", self._camera.rect_to_screen(t.rect))

        for b in self._bullets:
            pygame.draw.circle(screen, "green", self._camera.to_screen(b.position).xy, b.radius)

        bounding_box = self._camera.rect_to_screen(self._bounding_box.rect)
        pygame.draw.rect(screen, "white", bounding_box, 1)
        pygame.draw.rect(screen, "green", self._camera.screen_rect, 1)

        pygame.draw.circle(screen, "white", self._camera.to_screen(self._level.ship.position).xy,
                           self._level.ship.radius)

        screen.blit(self._level.shield_gauge.image, self._camera.to_screen(self._level.shield_gauge.position).xy)
        screen.blit(self._level.dark_matter_gauge.image,
                    (self._level.dark_matter_gauge.position + Vector(*self._camera.screen_rect.topleft, 0))[:2])

    def _get_next_track_direction(self, position, idx, track, loop=False, tolerance=1):
        target = track[idx]
        if (target - position).length_squared() < tolerance:
            idx += 1
            if idx < len(track):
                target = track[idx]
            else:
                target = position
                idx -= 1
                if loop:
                    idx = 0
                    target = track[idx]

        direction = target - position
        if direction:
            return direction.normalize(), idx
        return direction, idx


logger.debug("imported")
