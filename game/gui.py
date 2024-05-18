# -*- coding: utf-8 -*-

import logging

import pygame

from game import pygametext

logger = logging.getLogger(__name__)

logger.debug("importing...")


class Gauge:
    color = 'mediumpurple4'

    def __init__(self, size, initial, maximum, minimum):
        self.image = pygame.Surface(size)
        self.current = initial
        self.maximum = maximum
        self.minimum = minimum
        self.position = pygame.Vector3(10, 10, 0)

        self._previous = initial
        self.delta = 0
        self._dirty = True

        self._update_image()

    def increase(self, num):
        self.current += num
        if self.current > self.maximum:
            self.current = self.maximum
        self._dirty = True

    def decrease(self, num):
        self.current -= num
        if self.current < self.minimum:
            self.current = self.minimum
        self._dirty = True

    def update(self, dt):
        if self._dirty:
            self.delta = self._previous - self.current
            self._previous = self.current
            self._update_image()

    def _update_image(self):
        self.image.fill('red')
        rect = self.image.get_rect()
        gauge_rect = rect.inflate(-2, -2)
        gauge_center = gauge_rect.center
        pct = self.current / self.maximum
        gauge_rect.w *= pct
        gauge_rect.x = 1
        self.image.fill(self.color, gauge_rect)
        pygame.draw.rect(self.image, 'white', rect, width=1)
        self._previous = self.current
        if not hasattr(self, 'im_a_shield'):
            txt_img = pygametext.getsurf('DARK MATTER', None, fontsize=23, color='white',
                                         ocolor='black', owidth=1)
            txt_rect = txt_img.get_rect(center=gauge_center)
            self.image.blit(txt_img, txt_rect)
        self._dirty = False


class ShieldGauge(Gauge):
    color = 'green'
    heal = 1.0                  # units to heal per interval
    heal_interval = 0.5         # seconds
    interval_countdown = 0.5    # seconds
    dark_matter_gauge: Gauge = None    #
    im_a_shield = True

    def update(self, dt):
        transfer_amount = 0
        self.interval_countdown -= dt
        if self.interval_countdown <= 0.0:
            # if countdown exhausted...
            if self.current < self.maximum and self.dark_matter_gauge.current >= self.heal:
                # if shield needs healing, and dark matter is available...
                self.current += self.heal
                self.dark_matter_gauge.decrease(self.heal)
                transfer_amount = self.heal
                if self.current > self.maximum:
                    self.current = self.maximum
                self.interval_countdown += self.heal_interval
            else:
                # reset the countdown
                self.interval_countdown = self.heal_interval
            self._dirty = True

        if self._dirty:
            self.delta = self._previous - self.current
            self._previous = self.current
            self._update_image()
        return transfer_amount


if __name__ == '__main__':
    from pygame.locals import KEYDOWN, K_ESCAPE, K_x, QUIT

    pygame.init()
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode((400, 400))
    gauge = ShieldGauge((32, 9), 20, 20, 0)
    gauge.position.x = screen.get_width() / 2
    gauge.position.y = screen.get_height() / 2
    ups = 30
    while 1:
        clock.tick(ups)
        screen.fill((0, 0, 0))
        for e in pygame.event.get():
            if e.type == KEYDOWN:
                if e.key == K_ESCAPE:
                    quit()
                elif e.key == K_x:
                    gauge.decrease(1)
            elif e.type == QUIT:
                quit()
        gauge.update(1/ups)
        screen.blit(gauge.image, gauge.image.get_rect(center=gauge.position))
        pygame.display.flip()

logger.debug("imported")
