# -*- coding: utf-8 -*-
import functools
import logging
from typing import List

import pygame

from game.entities.entities import _Visible
from game.resourcespygame import ImageResource
from game.settings import Settings

logger = logging.getLogger(__name__)
logger.debug("importing...")


def _sort_func(x):
    return -x.layer


class GraphicsHandler:

    def __init__(self, screen_provider, resource_loader):
        self._resource_loader = resource_loader
        self._resource_map = {}
        self._screen_provider = screen_provider

    def initialize(self):
        self._initialize_window()

    def load_resources(self, resource_config):
        resources = self._resource_loader.load(resource_config)
        self._resource_map = resources

    @staticmethod
    def _initialize_window():
        pygame.display.set_mode(Settings.resolution)
        pygame.display.set_caption(Settings.caption)
        icon = pygame.image.load("resources/icon.png")
        pygame.display.set_icon(icon)

    def draw(self, screen, camera, game_time, entities: List[_Visible]):
        entities.sort(key=_sort_func)
        cam_scale = camera.ppu * camera._scale
        resource_map = self._resource_map
        get_transformed = self._get_transformed
        for e in reversed(entities):
            if e.special_draw_func is not None:
                e.special_draw_func(screen, camera, e, resource_map)
                continue

            res: ImageResource = resource_map[e.resource_id]
            count = res.count

            # animation update
            # if count > 1:
            if e.next_time < game_time:
                if e.next_time == 0:  # fixme hack: just to ensure all animations play well
                    e.next_time = game_time
                if res.resource_description.fps:
                    dt = 1 / res.resource_description.fps
                    delta = game_time - e.next_time + dt  # consider time since last update so at least 1 dt has passed!
                    e.next_time += dt
                    e.idx += int(delta // dt)  # skipped frames
                if not e.loop and e.idx >= count - 1:
                    if e.end_cb:
                        e.end_cb(e.cb_data, entities)
                e.idx = e.idx % count

            # prepare image to blit
            img: pygame.Surface = res.images[e.idx]

            # transform image if needed
            if e.alpha < 1 or e.scale != 1 or e.flip_x or e.flip_y or e.angle != 0:
                discrete_angle = int(e.angle) % 360  # int(round(e.angle)) % 360 # one degree resolution
                discrete_scale_x100 = int(e.scale * 100)  # int(round(e.scale * 100)) # x100 -> 2 digits precision
                discrete_alphax100 = int(e.alpha * 100)  # int(round(e.alpha * 100)) # x100
                img = get_transformed(img, discrete_alphax100, discrete_scale_x100, e.flip_x, e.flip_y, discrete_angle)

            # blit
            # screen_position = camera.to_screen(e.position)
            screen_position = e.position * cam_scale.elementwise() + camera.to_screen_translation
            r = img.get_rect(center=screen_position.xy)
            screen.blit(img, r)

    @staticmethod
    @functools.lru_cache(maxsize=1024)
    def _get_transformed(img: pygame.Surface, alpha_x100: int, scale_x100: int, flip_x: bool, flip_y: bool,
                         angle_degrees: int):
        """
        Transforms the image according to the arguments.
        :param img: the image to transform
        :param alpha_x100: the alpha value in range 100x of the float value. Range [0, 100]
        :param scale_x100: the scale value as an int, 100x, range (0, 10000?].
                To get the float back: s = scale_x100/100, range (0.0, 100.0?]
        :param flip_x: boolean to flip in x
        :param flip_y: boolean to flip in y
        :param angle_degrees: angle in degrees in range [0, 360)
        :return: transformed image
        """
        if alpha_x100 < 100:
            alpha = int(alpha_x100 / 100.0 * 255)
            img = img.copy()
            img.fill((255, 255, 255, alpha), None, pygame.BLEND_RGBA_MULT)
        if flip_x or flip_y:
            img = pygame.transform.flip(img, flip_x, flip_y)
        if scale_x100 != 100 or angle_degrees != 0:
            img = pygame.transform.rotozoom(img, angle_degrees, scale_x100 / 100.0)
        return img


if __name__ == "__main__":
    import pygame

    pygame.init()
    pygame.display.set_mode((800, 800))
    s = pygame.Surface((10, 10))
    r1 = GraphicsHandler._get_transformed(s, 90, 100, False, False, 0)
    r2 = GraphicsHandler._get_transformed(s, 80, 100, False, False, 0)
    if r1 == r2:
        print("gaa")


logger.debug("imported")
