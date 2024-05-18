# -*- coding: utf-8 -*-
import logging
from contextlib import contextmanager

import pygame
from pygame.math import Vector3 as Vector

logger = logging.getLogger(__name__)
logger.debug("importing...")


class Camera:

    def __init__(self, world_rect: pygame.Rect, screen_rect: pygame.Rect = None, ppu=1.0, speed=4):
        self._position = Vector(0, 0, 0)
        self.ppu = ppu
        self.world_rect = world_rect  # this is the visible area of the 'world'
        self._scale = Vector(1.0, 1.0, 1.0)
        self.screen_rect = pygame.Rect(0, 0, self.world_rect.w * self.ppu, self.world_rect.h * self.ppu)
        if screen_rect:
            self.screen_rect = screen_rect.copy()
            self._scale.x = screen_rect.w / world_rect.w  # s = w * f  -> f = s / w
            self._scale.y = screen_rect.h / world_rect.h
        self._screen_offset = Vector(*self.screen_rect.topleft, 0) + 0.5 * Vector(*self.screen_rect.size, 0)
        self.offset = Vector(0, 0, 0)  # to use with shake effects
        self.to_screen_translation = Vector(0, 0, 0)
        self.to_world_translation = Vector(0, 0, 0)
        self.speed = speed  # how fast it should lerp to new position

        self.look_at(self._position)  # update values

        # note: offset contains ppu multiplication
        #
        # world -> screen: screen = (world - cam * parallax) * ppu + offset
        #                         = world * ppu - cam * parallax * ppu + offset
        # screen -> world:  world = (screen - offset) / ppu + cam * parallax
        #                         = screen / ppu - offset / ppu + cam * parallax

        # fixme: after pyweek: self._scale and ppu contradict each other...!


    def look_at(self, world_position):
        self._position = world_position.copy()
        self.world_rect.center = round(world_position.x), round(world_position.y)
        self.to_screen_translation = -(
                    (self._position + self.offset) * self.ppu * self._scale.elementwise()) + self._screen_offset
        self.to_world_translation = - (self._screen_offset / (self.ppu * self._scale).elementwise()) + (
                    self._position - self.offset)

    def scale_to_screen(self, distance, direction: Vector):  # fixme: after pyweek not sure if this is correct!!
        p2 = direction.normalize() * distance * self.ppu * self._scale.elementwise()
        return p2.length()

    def rect_to_screen(self, rect: pygame.Rect):
        rect.normalize()  # ensure topleft is topleft ant bottomright is bottom right
        top_left = self.to_screen(Vector(*rect.topleft, 0))
        bottom_right = self.to_screen(Vector(*rect.bottomright, 0))
        return pygame.Rect(top_left.xy, (bottom_right - top_left).xy)

    def to_screen(self, world_pos, parallax=None):
        if parallax:
            scale = self.ppu * self._scale
            scale1 = scale.elementwise()
            x, y, z = (world_pos - (self._position + self.offset) * parallax.elementwise()) * scale1 \
                      + self._screen_offset
            return pygame.math.Vector2(round(x), round(y))
        x, y, z = world_pos * self.ppu * self._scale.elementwise() + self.to_screen_translation
        return pygame.math.Vector2(round(x), round(y))

    def to_world(self, screen_pos, parallax=None):
        if parallax:
            scale = self.ppu * self._scale
            p = pygame.math.Vector2(screen_pos)
            scale1 = scale.elementwise()
            return (Vector(*p, 0) - self._screen_offset) / scale1 \
                + (self._position + self.offset) * parallax.elementwise()
        p = pygame.math.Vector2(screen_pos)
        return Vector(*p, 0) / (self.ppu * self._scale).elementwise() + self.to_world_translation

    def lerp(self, point, dt_s):
        """
        Linear interpolation to the given point.
        :param point: The point where the camera should be when t=1.0
        :param dt_s: interpolation factor, t=0 -> self.position, t=1 -> point
        """
        # see for accurate lerp: https://en.wikipedia.org/wiki/Linear_interpolation
        # float lerp(float v0, float v1, float t) {
        #   return (1 - t) * v0 + t * v1;
        # }
        t = self.speed * dt_s
        t = 1 if t > 1 else (0 if t < 0 else t)
        new_position = (1 - t) * self._position + t * point
        self.look_at(new_position)

    @contextmanager
    def clip(self, screen: pygame.Surface):
        orig_clip = screen.get_clip()
        screen.set_clip(self.screen_rect)
        try:
            yield screen
        finally:
            screen.set_clip(orig_clip)


if __name__ == "__main__":
    world_rect = pygame.Rect(0, 0, 100, 100)
    wp = Vector(10, 10, 0)
    cam = Camera(world_rect)
    cam.look_at(Vector(50, 50, 0))
    sp = cam.to_screen(wp)
    wp1 = cam.to_world(sp)
    print("default", wp, sp, wp1, "origin screen", cam.to_screen(Vector(0, 0, 0)), "wr", cam.world_rect, "sr",
          cam.screen_rect)

    cam = Camera(world_rect, ppu=2.0)
    cam.look_at(Vector(50, 50, 0))
    sp = cam.to_screen(wp)
    wp1 = cam.to_world(sp)
    print("ppu", wp, sp, wp1, "origin screen", cam.to_screen(Vector(0, 0, 0)), "wr", cam.world_rect, "sr",
          cam.screen_rect)

    cam = Camera(world_rect)
    cam.look_at(Vector(50, 50, 0))
    parallax_f = Vector(2.0, 0.5, 1.0)
    sp = cam.to_screen(wp, parallax=parallax_f)
    wp1 = cam.to_world(sp, parallax=parallax_f)
    print("parallax", wp, sp, wp1, "origin screen", cam.to_screen(Vector(0, 0, 0)), "wr", cam.world_rect, "sr",
          cam.screen_rect)

    import pygame
    from pygame.math import Vector3 as V

    pygame.init()
    pygame.font.init()

    screen = pygame.display.set_mode((1024, 768))
    font = pygame.font.Font(None, 40)

    top = pygame.Surface((500, 100), pygame.SRCALPHA)
    c = pygame.Color("cyan", a=128)
    c.a = 128
    top.fill(c, None, pygame.BLEND_RGBA_ADD)
    label = font.render("top 1.25 ", True, "black")
    top.blit(label, (0, 0))

    front2 = pygame.Surface((500, 200), pygame.SRCALPHA)
    c = pygame.Color("mediumseagreen", a=128)
    c.a = 128
    front2.fill(c, None, pygame.BLEND_RGBA_ADD)
    label = font.render("front without paralls " * 5, True, "black")
    front2.blit(label, (0, 0))

    front = pygame.Surface((500, 200), pygame.SRCALPHA)
    c = pygame.Color("mediumseagreen", a=128)
    c.a = 128
    front.fill(c, None, pygame.BLEND_RGBA_ADD)
    label = font.render("front 1.0 " * 5, True, "black")
    front.blit(label, (0, 0))

    mid = pygame.Surface((500, 400), pygame.SRCALPHA)
    c = pygame.Color("sandybrown", a=128)
    c.a = 128
    mid.fill(c, None, pygame.BLEND_RGBA_ADD)
    label = font.render("mid 0.75 " * 5, True, "black")
    mid.blit(label, (0, 0))

    back = pygame.Surface((500, 500))
    c = pygame.Color("grey")
    back.fill(c, None, pygame.BLEND_RGBA_ADD)
    label = font.render("back 0.5 " * 5, True, "black")
    back.blit(label, (0, 0))

    world_rect = pygame.Rect(0, 0, 500, 500)
    cam = Camera(world_rect)

    clock = pygame.time.Clock()
    running = True
    focus = V(0, -250, 0)
    step = 5
    while running:
        clock.tick(60)
        for e in pygame.event.get():
            if e.type == pygame.QUIT or (e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE):
                running = False
            # elif e.type == pygame.KEYDOWN:
            #     if e.key == pygame.K_RIGHT:
            #         focus.x += step
            #     elif e.key == pygame.K_LEFT:
            #         focus.x -= step
        # update
        pressed = pygame.key.get_pressed()
        p_r = pressed[pygame.K_RIGHT]
        p_l = pressed[pygame.K_LEFT]
        focus += V(p_r - p_l, 0, 0) * 1
        cam.look_at(focus)

        # draw
        screen.fill("black")

        pos = V(0, 0, 0)
        screen.blit(back, back.get_rect(bottomleft=cam.to_screen(pos, V(0.5, 1.0, 1.0)).xy))
        screen.blit(mid, mid.get_rect(bottomleft=cam.to_screen(pos, V(0.75, 1.0, 1.0)).xy))
        screen.blit(front, front.get_rect(bottomleft=cam.to_screen(pos, V(1.0, 1.0, 1.0)).xy))
        screen.blit(front2, front.get_rect(bottomleft=cam.to_screen(pos).xy))
        screen.blit(top, top.get_rect(bottomleft=cam.to_screen(pos, V(1.25, 1.0, 1.0)).xy))

        # draw origin and axis
        origin_screen = cam.to_screen(V(0, 0, 0)).xy
        pygame.draw.circle(screen, "white", origin_screen, 3)
        vec_len = 20
        pygame.draw.line(screen, "red", origin_screen, cam.to_screen(vec_len * V(1, 0, 0)).xy)
        pygame.draw.line(screen, "green", origin_screen, cam.to_screen(vec_len * V(0, 1, 0)).xy)

        # draw focus
        pygame.draw.circle(screen, "yellow", cam.to_screen(focus).xy, 3)

        # screen rect
        pygame.draw.rect(screen, "white", cam.screen_rect, 1)

        pygame.display.flip()

logger.debug("imported")
