# -*- coding: utf-8 -*-
import logging
import os
from dataclasses import dataclass, field
from typing import List, Tuple

import pygame

from game.resources import BaseResource, AbstractBaseLoader, AbstractResourceDescription

logger = logging.getLogger(__name__)
logger.debug("importing...")


@dataclass
class SoundResourceDescription(AbstractResourceDescription):
    """the filename to load"""
    filename: str
    """any free channel if None, otherwise use reserved channel"""
    channel_id: int = None
    """predefined volume from resource loading to level out different sound volumes"""
    volume: float = 1.0
    """replace other sound that is playing, otherwise do not play (used as force flag if channel_id is None)"""
    replace: bool = True


@dataclass
class SoundResource(BaseResource):
    channel_id: int
    volume: float
    replace: bool
    sound: pygame.mixer.Sound


class SoundLoader(AbstractBaseLoader):

    def load(self, resource_description: SoundResourceDescription) -> SoundResource:
        rd = resource_description
        sound = pygame.mixer.Sound(rd.filename)
        sound.set_volume(rd.volume)
        return SoundResource(rd, rd.channel_id, rd.volume, rd.replace, sound)


@dataclass
class MusicResourceDescription(AbstractResourceDescription):
    filename: str
    volume: float = 1.0


@dataclass
class MusicResource(BaseResource):
    pass


class MusicLoader(AbstractBaseLoader):
    def load(self, resource_description: MusicResourceDescription) -> MusicResource:
        return MusicResource(resource_description)


@dataclass
class ImageResourceDescription(AbstractResourceDescription):
    filename: str
    flip_x: bool = False
    flip_y: bool = False
    fps: float = 0


@dataclass
class ImageResource(BaseResource):
    images: List[pygame.Surface]
    fps: float
    loop: bool
    count: int


class ImageLoader(AbstractBaseLoader):

    def load(self, resource_description: ImageResourceDescription) -> ImageResource:
        image = pygame.image.load(resource_description.filename).convert_alpha()
        image = pygame.transform.flip(image, resource_description.flip_x, resource_description.flip_y)
        return ImageResource(resource_description, [image], 0, False, 1)


@dataclass
class _AnimationResourceDescription(AbstractResourceDescription):
    fps: float
    loop: bool = field(default=True, kw_only=True)


@dataclass
class AnimationResourceDescription(_AnimationResourceDescription):
    filename: str
    rect: Tuple[int, int, int, int]
    row_count: int
    col_count: int
    slice: Tuple[int] = None
    flip_x: bool = False
    flip_y: bool = False


class AnimationResourceLoader(AbstractBaseLoader):
    def load(self, resource_description: AnimationResourceDescription) -> ImageResource:
        image = pygame.image.load(resource_description.filename).convert_alpha()
        r = pygame.Rect(resource_description.rect)
        idx = 0
        indexed_images = {}  # {idx:image}
        for y in range(resource_description.row_count):
            for x in range(resource_description.col_count):
                i = pygame.Surface(r.size, pygame.SRCALPHA)
                i.blit(image, (0, 0), r.move(x * r.w, y * r.h))
                i = pygame.transform.flip(i, resource_description.flip_x, resource_description.flip_y)
                indexed_images[idx] = i
                idx += 1

        images = []
        if resource_description.slice:
            image_order = resource_description.slice
        else:
            image_order = sorted(indexed_images.keys())

        for idx in image_order:
            images.append(indexed_images[idx])

        return ImageResource(resource_description, images, resource_description.fps, resource_description.loop,
                             len(images))


@dataclass
class FileListResourceDescription(_AnimationResourceDescription):
    path_to_dir: str
    file_names: List[str]
    flip_x: bool = False
    flip_y: bool = False


class FileListResourceLoader(AbstractBaseLoader):
    def load(self, resource_description: FileListResourceDescription) -> ImageResource:
        images = []
        for filename in resource_description.file_names:
            path = os.path.join(resource_description.path_to_dir, filename)
            image = pygame.image.load(path).convert_alpha()
            image = pygame.transform.flip(image, resource_description.flip_x, resource_description.flip_y)
            images.append(image)
        return ImageResource(resource_description, images, resource_description.fps, resource_description.loop,
                             len(images))


@dataclass
class DirectoryResourceDescription(_AnimationResourceDescription):
    path_to_dir: str
    extension: str = "png"
    flip_x: bool = False
    flip_y: bool = False


class DirectoryResourceLoader(AbstractBaseLoader):
    def load(self, resource_description: DirectoryResourceDescription) -> ImageResource:
        images = []
        import glob
        search = os.path.join(resource_description.path_to_dir, f"*.{resource_description.extension}")
        for f in sorted(glob.glob(search)):
            image = pygame.image.load(f).convert_alpha()
            image = pygame.transform.flip(image, resource_description.flip_x, resource_description.flip_y)
            images.append(image)
        return ImageResource(resource_description, images, resource_description.fps, resource_description.loop,
                             len(images))


@dataclass
class FakeImageDescription(AbstractResourceDescription):
    size: (int, int)
    color: pygame.Color
    fps: float = 0


class FakeImageLoader(AbstractBaseLoader):

    def load(self, resource_description: FakeImageDescription) -> ImageResource:
        surf = pygame.Surface(resource_description.size)
        surf.fill(resource_description.color)
        return ImageResource(resource_description, [surf], 0, False, 1)


logger.debug("imported")
