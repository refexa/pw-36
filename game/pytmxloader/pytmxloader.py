# -*- coding: utf-8 -*-
#
# New BSD license
#
# Copyright (c) DR0ID
# This file is part of pytmxloader
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# * Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
# * Neither the name of the <organization> nor the
# names of its contributors may be used to endorse or promote products
# derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL DR0ID BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""
TODO: module description


Versioning scheme based on: http://en.wikipedia.org/wiki/Versioning#Designating_development_stage

::

      +-- api change, probably incompatible with older versions
      |     +-- enhancements but no api change
      |     |
    major.minor[.build[.revision]]
                   |        |
                   |        +-|* x for x bugfixes
                   |
                   +-|* 0 for alpha (status)
                     |* 1 for beta (status)
                     |* 2 for release candidate
                     |* 3 for (public) release

.. versionchanged:: 4.0.0.0
    initial version


UML in ASCII ( see: http://c2.com/cgi/wiki?UmlAsciiArt and see https://en.wikipedia.org/wiki/Class_diagram )

    Association:   ^   Aggregation:    O   Composition:    @   Inheritance:    #
                |                   |                   |                   |
              <-+->               O-+-O               @-+-@               #-+-#
                |                   |                   |                   |
                V                   O                   @                   #

    Multiplicity
    0       No instances (rare)
    0..1    No instances, or one instance
    1       Exactly one instance
    0..*    Zero or more instances
    *       Zero or more instances
    1..*    One or more instances


                                        +-------------------+
                                        |   TilesetInfo     |
                                        +-------------------+
                                        |                   |
                                        |                   |
                                        +-------------------+
                                              1 |
                                                |       +-----------------------------------------------+
                                           1..* O       | 1                                             |
        +-------------------+           +-------------------+           +-----------------------+       |
        |   MapInfo         |           |   TileInfo        |           |   AnimationFrameInfo  |       |
        +-------------------+ 1       * +-------------------+ 1       * +-----------------------+       |
        |                   |O----------|                   |O----------|                       |       |
        |                   |           |                   |           |                       |       |
        +-------------------+           +-------------------+           +-----------------------+       |
                O 1                             | 1     | 1                         O *                 |
                |                               |       |                           |                   |
                |                               |       +---------------------------+                   |
                |                               |                                                       |
                | *                             O *                                                     |
        +-------------------+           +-----------------------+                                       |
        |   LayerInfo       |           |   TileLayerTileInfo   |                                       |
        +-------------------+           +-----------------------+ *                                     |
        |                   |           |                       |-----------------------+               |
        |                   |           |                       |                       |               |
        +-------------------+           +-----------------------+                       |               |
                    #                                                                   |               |
                    |                                                                   |               |
                +---+---------------------------+------------------------------+        |               |
                |                               |                              |        O 1             |
        +-----------------------+       +-----------------------+       +-----------------------+       |
        |    ObjectLayerInfo    |       |    ImageLayerInfo     |       |    TileLayerInfo      |       |
        +-----------------------+       +-----------------------+       +-----------------------+       |
        |                       |       |                       |       |                       |       |
        |                       |       |                       |       |                       |       |
        +-----------------------+       +-----------------------+       +-----------------------+       |
                O 1                                                                                     |
                |                                                                                       |
                | *                                                                                     |
        +-----------------------+       +-----------------------+       +-----------------------+ *     |
        |    ObjectBaseInfo     |       |    ObjectPolyLineInfo |       |    ObjectTileInfo     |O------+
        +-----------------------+       +-----------------------+       +-----------------------+
        |                       |       |                       |       |                       |
        |                       |       |                       |       |                       |
        +-----------------------+       +-----------------------+       +-----------------------+
                    #                           |                               |
                    |                           |                               |
                +---+---------------------------+-------------------------------+
                |                               |                               |
        +-----------------------+       +-----------------------+       +-----------------------+
        |  ObjectRectangleInfo  |       |    ObjectEllipseInfo  |       |    ObjectPolygonInfo  |
        +-----------------------+       +-----------------------+       +-----------------------+
        |                       |       |                       |       |                       |
        |                       |       |                       |       |                       |
        +-----------------------+       +-----------------------+       +-----------------------+

"""
import base64
import codecs
import gzip
import json
import os
import struct
import sys
import zlib

import math
from xml.etree.ElementTree import ElementTree

from .comparison import EquatableMixin

try:
    # noinspection PyUnresolvedReferences
    from io import StringIO, BytesIO
except ImportError:
    # noinspection PyUnresolvedReferences
    from StringIO import StringIO

__version__ = '4.1.0.0'

# for easy comparison as in sys.version_info but digits only
__version_info__ = tuple([int(d) for d in __version__.split('.')])

__author__ = 'DR0ID'
__email__ = 'dr0iddr0id [at] googlemail [dot] com'
__copyright__ = "DR0ID @ 2020"
__credits__ = ["DR0ID", "Gumbumm"]  # list of contributors
__maintainer__ = "DR0ID"
__license__ = "New BSD license"

# list of public visible parts of this module
__all__ = [
    "load_map_from_file_path", "load_map_from_file_like", "load_map_from_json_string",
    "LayerInfo", "TileLayerInfo", "ObjectLayerInfo", "ImageLayerInfo",
    "MapInfo", "TileInfo", "TilesetInfo", "AnimationFrameInfo",
    "ObjectRectangleInfo", "ObjectEllipseInfo", "ObjectPolygonInfo", "ObjectPolylineInfo", "ObjectTileInfo",
    "VersionException", "InternalError", "MissingFileTypeException", "UnknownFileExtensionException",
    "TILE_LAYER_TYPE", "IMAGE_LAYER_TYPE", "OBJECT_LAYER_TYPE",
    "rotate_point",
]

_FLIP_BITS_H = 0x80000000  # 1 << 31
_FLIP_BITS_V = 0x40000000  # 1 << 30
_FLIP_BITS_D = 0x20000000  # 1 << 29
_NO_BITS_0x0 = 0
# ROTATED90 = _FLIP_BITS_D | _FLIP_BITS_H
# ROTATED180 = _FLIP_BITS_V | _FLIP_BITS_H
# ROTATED270 = _FLIP_BITS_D | _FLIP_BITS_V
_ALL_FLIP_BITS = _FLIP_BITS_D | _FLIP_BITS_H | _FLIP_BITS_V

# D V H
# 1 1 1     270° -> H
# 1 1 0 270°
# 1 0 1  90°
# 1 0 0     90° -> H
# 0 1 1 180°
# 0 1 0     V
# 0 0 1     H
# 0 0 0   0°
_flag_to_rot_flips = {
    _FLIP_BITS_D | _FLIP_BITS_V | _FLIP_BITS_H: (270, False, True),
    _FLIP_BITS_D | _FLIP_BITS_V | _NO_BITS_0x0: (270, False, False),
    _FLIP_BITS_D | _NO_BITS_0x0 | _FLIP_BITS_H: (90, False, False),
    _FLIP_BITS_D | _NO_BITS_0x0 | _NO_BITS_0x0: (90, False, True),
    _NO_BITS_0x0 | _FLIP_BITS_V | _FLIP_BITS_H: (180, False, False),
    _NO_BITS_0x0 | _FLIP_BITS_V | _NO_BITS_0x0: (0, True, False),
    _NO_BITS_0x0 | _NO_BITS_0x0 | _FLIP_BITS_H: (0, False, True),
    _NO_BITS_0x0 | _NO_BITS_0x0 | _NO_BITS_0x0: (0, False, False),
}

# noinspection SpellCheckingInspection
#: The constant for the tile layer type.
TILE_LAYER_TYPE = "tilelayer"
# noinspection SpellCheckingInspection
#: The constant for the image layer type.
IMAGE_LAYER_TYPE = "imagelayer"
# noinspection SpellCheckingInspection
#: The constant for the object layer type.
OBJECT_LAYER_TYPE = "objectgroup"


class VersionException(Exception):
    """Exception raised when a unknown version of a map has been loaded and it can't be processed."""
    pass


class InternalError(Exception):
    """Internal error indicating something has really cone wrong!"""
    pass


class MissingFileTypeException(Exception):
    """Exception raise if neither the file has an extension (e.g. '.json' nor a file_type_hint is given."""
    pass


class UnknownFileExtensionException(Exception):
    """Raised when the file extension is unknown."""
    pass

# TODO: update unittest for gid
class TileInfo(EquatableMixin):
    def __init__(self, gid, tileset, spritesheet_x, spritesheet_y, properties, angle=0, flip_x=False, flip_y=False,
                 probability=1.0, animation=None, tile_type=None):
        """
        Container for the data of a tile in a tileset.

        :param tileset: a reference to :class:`.TilesetInfo`.
        :param spritesheet_x: the x coordinate in the spritesheet (using topleft as origin).
        :param spritesheet_y: the y coordinate in the spritesheet (using topleft as origin).
        :param properties: a dictionary containing the properties {string: string}.
        :param angle: the rotation angle in degrees (normally multiples of 90°).
        :param flip_x: True if the image is flipped in x direction, otherwise not.
        :param flip_y: True if the image is flipped in y direction, otherwise not.
        :param probability: the probability for the terrain tool, range [0.0, 1.0]
        :param animation: list of animation frames if any, otherwise None.
        :param tile_type: the value of the type property.
        """
        self.animation = animation
        self.probability = probability
        self.tileset = tileset  # TilesetInfo
        self.flip_x = flip_x
        self.flip_y = flip_y
        self.angle = angle
        self.properties = properties
        self.spritesheet_x = spritesheet_x
        self.spritesheet_y = spritesheet_y
        self.gid = gid
        self.type = tile_type

    def __eq__(self, other):
        if isinstance(other, TileInfo):
            return (self.tileset, self.flip_x, self.flip_y, self.angle, self.properties,
                    self.spritesheet_x, self.spritesheet_y, self.probability, self.animation) == (
                       other.tileset, other.flip_x, other.flip_y,
                       other.angle, other.properties,
                       other.spritesheet_x, other.spritesheet_y, other.probability, other.animation)
        return NotImplemented


class TileLayerTileInfo(EquatableMixin):
    def __init__(self, tile_x, tile_y, tile_info, offset_x, offset_y):
        """
        Container for the data of a layer tile.

        :param tile_x: the tile x position in pixels
        :param tile_y: the tile y position in pixels.
        :param tile_info: reference to :class:`.TileInfo`.
        :param offset_x: the offset in pixels defining the top (used to render using topleft as origin)
        :param offset_y: the  offset in pixels defining the left (used to render using topleft as origin)
        """
        self.tile_x = tile_x  # TODO: rename to pixel_pos_x or similar?
        self.tile_y = tile_y  # TODO: rename to pixel_pos_y or similar?
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.tile_info = tile_info  # TileInfo

    def __eq__(self, other):
        if isinstance(other, TileLayerTileInfo):
            return (self.tile_info, self.tile_x, self.tile_y, self.offset_x, self.offset_y) == \
                   (other.tile_info, other.tile_x, other.tile_y, other.offset_x, other.offset_y)
        return NotImplemented


class AnimationFrameInfo(EquatableMixin):
    def __init__(self, tile_info, duration):
        """
        The AnimationFrameInfo holds the reference to a tile info and the duration in ms how long this image is shown.
        :param tile_info: reference to the tile info.
        :param duration: the duration of this frame in milliseconds.
        """
        self.tile_info = tile_info
        self.duration = duration

    def __eq__(self, other):
        if isinstance(other, AnimationFrameInfo):
            # the tile info needs to be compared without the animation because it can reference the same tile info
            return self.duration == other.duration and \
                   (self.tile_info.tileset, self.tile_info.flip_x, self.tile_info.flip_y, self.tile_info.angle,
                    self.tile_info.properties,
                    self.tile_info.spritesheet_x, self.tile_info.spritesheet_y, self.tile_info.probability) == (
                       other.tile_info.tileset, other.tile_info.flip_x, other.tile_info.flip_y,
                       other.tile_info.angle, other.tile_info.properties,
                       other.tile_info.spritesheet_x, other.tile_info.spritesheet_y, other.tile_info.probability)
        return NotImplemented


class TilesetInfo(EquatableMixin):
    def __init__(self, name, tile_width, tile_height, properties, image_path_rel_to_map, image_path_rel_to_cwd,
                 first_gid, transparent_color, pixel_offset_x, pixel_offset_y):
        """
        Container for the data of a tileset.

        :param name: name of the tileset.
        :param tile_width: the width of the tileset in pixels.
        :param tile_height: the height of the tileset in pixels.
        :param properties: the properties as a dict like {string: string}.
        :param image_path_rel_to_map: the filename of the image.
        :param image_path_rel_to_cwd: the image path relative to the current working directory. Might be None!
        :param first_gid: the starting gid of this tileset.
        :param transparent_color: the transparent color used int this tileset.
        :param pixel_offset_x: the offset in pixels
        :param pixel_offset_y: the offset in pixels
        """
        self.pixel_offset_x = pixel_offset_x
        self.pixel_offset_y = pixel_offset_y
        self.name = name
        self.tile_width = tile_width
        self.tile_height = tile_height
        self.properties = properties
        self.image_path_rel_to_map = image_path_rel_to_map
        self.image_path_rel_to_cwd = image_path_rel_to_cwd
        self.first_gid = first_gid
        self.transparent_color = transparent_color

    def __eq__(self, other):
        if isinstance(other, TilesetInfo):
            return (self.name, self.tile_width, self.tile_height, self.properties, self.image_path_rel_to_map,
                    self.first_gid, self.transparent_color, self.pixel_offset_x, self.pixel_offset_y) == (
                       other.name, other.tile_width, other.tile_height,
                       other.properties, other.image_path_rel_to_map, other.first_gid,
                       other.transparent_color, other.pixel_offset_x, other.pixel_offset_y)
        return NotImplemented


class LayerInfo(EquatableMixin):
    def __init__(self, layer_type, properties, name, visible, opacity, width, height, tile_offset_x, tile_offset_y,
                 pixel_offset_x, pixel_offset_y):
        """
        Base class for all layer info containers.

        :param name: the name of the layer
        :param pixel_offset_x: the offset in x (in pixels?)
        :param pixel_offset_y: the offset in pixel_offset_y (in pixels?)
        :param width: number of tiles in x direction.
        :param height: number of tiles in y direction.
        :param visible: True if the layer is visible, otherwise False.
        :param opacity: opacity factor, 0 fully transparent, 1 opaque.
        :param tile_offset_x: offset in number of tiles for x
        :param tile_offset_y: offset in number of tiles for y
        :param properties: the properties of the layer.
        :param layer_type: the type of the layer as string.
        """
        self.properties = properties
        self.layer_type = layer_type
        self.name = name
        self.pixel_offset_x = pixel_offset_x
        self.pixel_offset_y = pixel_offset_y
        self.width = width
        self.height = height
        self.visible = visible
        self.opacity = opacity
        self.tile_offset_x = tile_offset_x
        self.tile_offset_y = tile_offset_y

    def __eq__(self, other):
        if isinstance(other, LayerInfo):
            return (self.properties,
                    self.layer_type,
                    self.name,
                    self.pixel_offset_x,
                    self.pixel_offset_y,
                    self.width,
                    self.height,
                    self.visible,
                    self.opacity,
                    self.tile_offset_x,
                    self.tile_offset_y) == (other.properties,
                                            other.layer_type,
                                            other.name,
                                            other.pixel_offset_x,
                                            other.pixel_offset_y,
                                            other.width,
                                            other.height,
                                            other.visible,
                                            other.opacity,
                                            other.tile_offset_x,
                                            other.tile_offset_y)
        return NotImplemented


class TileLayerInfo(LayerInfo):
    def __init__(self, name, pixel_offset_x, pixel_offset_y, width, height, tile_w, tile_h, visible, opacity, data,
                 layer_properties, tile_offset_x, tile_offset_y):
        # noinspection SpellCheckingInspection
        """
        Container for the data of a tile layer.

        :param layer_properties: the properties for this layer.
        :param name: the name of the layer
        :param pixel_offset_x: the offset in x (in pixels?)
        :param pixel_offset_y: the offset in pixel_offset_y (in pixels?)
        :param width: number of tiles in x direction.
        :param height: number of tiles in y direction.
        :param tile_w: the tile width in pixels.
        :param tile_h: the tile height in pixels.
        :param visible: True if the layer is visible, otherwise False.
        :param opacity: opacity factor, 0 fully transparent, 1 opaque.
        :param data: the tiles of the map. Caution: data_yx[y][x] is the correct access.
        :param tile_offset_x: offset in number of tiles for x
        :param tile_offset_y: offset in number of tiles for y
        """
        LayerInfo.__init__(self, TILE_LAYER_TYPE, layer_properties, name, visible, opacity, width, height,
                           tile_offset_x, tile_offset_y, pixel_offset_x, pixel_offset_y)
        self.tile_w = tile_w
        self.tile_h = tile_h
        self.data_yx = data  # [y][x] -> TileLayerTileInfo

    def __eq__(self, other):
        if isinstance(other, TileLayerInfo):
            return LayerInfo.__eq__(self, other) and \
                   self.tile_w == other.tile_w and self.tile_h == other.tile_h and self.data_yx == other.data_yx
        return NotImplemented


class ObjectLayerInfo(LayerInfo):
    def __init__(self, name, pixel_offset_x, pixel_offset_y, width, height, visible, opacity,
                 layer_properties, tile_offset_x, tile_offset_y, draw_order, objects):
        """
        Container for the data of a tile layer.

        :param draw_order: defines the draw order of the objects
        :param objects: a list of ObjectInfo instances.
        :param layer_properties: the properties for this layer.
        :param name: the name of the layer
        :param pixel_offset_x: the offset in x (in pixels?)
        :param pixel_offset_y: the offset in pixel_offset_y (in pixels?)
        :param width: number of tiles in x direction.
        :param height: number of tiles in y direction.
        :param visible: True if the layer is visible, otherwise False.
        :param opacity: opacity factor, 0 fully transparent, 1 opaque.
        :param tile_offset_x: offset in number of tiles for x
        :param tile_offset_y: offset in number of tiles for y
        """
        LayerInfo.__init__(self, OBJECT_LAYER_TYPE, layer_properties, name, visible, opacity, width, height,
                           tile_offset_x, tile_offset_y, pixel_offset_x, pixel_offset_y)
        self.objects = objects
        self.draw_order = draw_order
        self.rectangles = [_o for _o in objects if isinstance(_o, ObjectRectangleInfo)]
        self.ellipses = [_o for _o in objects if isinstance(_o, ObjectEllipseInfo)]
        self.polygons = [_o for _o in objects if isinstance(_o, ObjectPolygonInfo)]
        self.poly_lines = [_o for _o in objects if isinstance(_o, ObjectPolylineInfo)]
        self.tiles = [_o for _o in objects if isinstance(_o, ObjectTileInfo)]

    def __eq__(self, other):
        if isinstance(other, ObjectLayerInfo):
            return LayerInfo.__eq__(self, other) and \
                   self.objects == other.objects and self.draw_order == other.draw_order
        return NotImplemented


class ImageLayerInfo(LayerInfo):
    def __init__(self, name, pixel_offset_x, pixel_offset_y, width, height, visible, opacity,
                 layer_properties, image_path_rel_to_map, image_path_rel_to_cwd):
        """
        Container for the data of a tile layer.

        :param image_path_rel_to_map:
        :param image_path_rel_to_cwd:
        :param layer_properties: the properties for this layer.
        :param name: the name of the layer
        :param pixel_offset_x: the offset in x (in pixels?)
        :param pixel_offset_y: the offset in pixel_offset_y (in pixels?)
        :param width: number of tiles in x direction.
        :param height: number of tiles in y direction.
        :param visible: True if the layer is visible, otherwise False.
        :param opacity: opacity factor, 0 fully transparent, 1 opaque.
        """
        LayerInfo.__init__(self, IMAGE_LAYER_TYPE, layer_properties, name, visible, opacity, width, height,
                           0, 0, pixel_offset_x, pixel_offset_y)
        self.image_path_rel_to_cwd = image_path_rel_to_cwd
        self.image_path_rel_to_map = image_path_rel_to_map

    def __eq__(self, other):
        if isinstance(other, ImageLayerInfo):
            return LayerInfo.__eq__(self, other) and \
                   self.image_path_rel_to_cwd == other.image_path_rel_to_cwd and \
                   self.image_path_rel_to_map == other.image_path_rel_to_map
        return NotImplemented


# TODO: write method to retrieve all images to load (as a set!) ??
class MapInfo(EquatableMixin):
    def __init__(self, layers, tiles, properties):
        # noinspection SpellCheckingInspection
        """
        Container for the map data. The tiles dictionary contains all tiles using the gid (global id) key.
        The gid is defined in the tilesets. Additional gids are added for the rotated and/or flipped tiles.

        :param properties: the properties of the map
        :param layers: list of layers, see :class:`.LayerInfo`. The layers can be differentiated
            by the layer_type attribute. The different layers contain different data. They are in the same
            order as in the map file which is also the render order.
        :param tiles: a dictionary containing information about the tiles as {gid: :class:`.TileInfo`}.
        """
        self.properties = properties
        self.tiles = tiles  # {gid : TileInfo}
        self.layers = layers  # [LayerInfo]

    def __eq__(self, other):
        if isinstance(other, MapInfo):
            return self.layers == other.layers and self.tiles == other.tiles and self.properties == other.properties
        return NotImplemented


# TODO: allow tmx files to be passed in, add an file type hint (default: None -> guess from file extension)
def load_map_from_file_path(file_path, file_type_hint=None, encoding="ascii", load_visible_only=False):
    """
    Loads the map from file and returns a :class:`.MapInfo` object.

    :param encoding: The encoding used to load the file. Defaults to 'ascii'.
    :param file_path: the file path to the file.
    :param file_type_hint: Normally the file type is derived from the file extension. If the file extension is not
        clear or misleading, then this hint defines how it is tried to load it, e.g. ".json" for a json file.
        Supported formats so far are: *.json
        Default: None
    :returns :class:`.MapInfo` object containing loaded data.
    """
    # todo check allowed map versions!
    if not os.path.isfile(file_path):
        raise UnknownFileExtensionException("'file_path' should be a file, not a directory.")

    file_type_hint = _get_file_type_hint(file_path, file_type_hint)

    with codecs.open(file_path, encoding=encoding) as map_file:
        return load_map_from_file_like(map_file, file_path, file_type_hint, encoding, load_visible_only)


def load_map_from_json_string(data_as_string, file_path=None, file_type_hint=None, encoding="ascii", load_visible_only=False):
    """
    Loads the map from a json formatted string.

    :param data_as_string: the json string to load.
    :param file_path: optional the file path to the file. If not provided, then the
        :class:`.TilesetInfo.image_path_rel_to_cwd` will be None. A relative path to the directory where the images
        are relative to can be passed in instead.
    :param file_type_hint: Normally the file type is derived from the file extension. If the file extension is not
        clear or misleading, then this hint defines how it is tried to load it, e.g. ".json" for a json file.
        Supported formats so far are: *.json
        Default: None
    :param encoding: The encoding used to read the file. Defaults to 'ascii'.
    :returns :class:`.MapInfo` object containing loaded data.
    """
    file_type_hint = _get_file_type_hint(file_path, file_type_hint)

    if file_type_hint == ".json":
        map_data = json.loads(data_as_string)
        return load_map_from_data(map_data, file_path, load_visible_only)

    raise UnknownFileExtensionException("Unknown file type, supported are: '.json'")


def load_map_from_file_like(file_like_object, file_path=None, file_type_hint=None, encoding="ascii", load_visible_only=False):
    """
    Loads the map from a file like object and returns a :class:`.MapInfo` object.

    :param file_like_object: the file like object to load the data from.
    :param file_path: optional the file path to the file. If not provided, then the
        :class:`.TilesetInfo.image_path_rel_to_cwd` will be None. A relative path to the directory where the images
        are relative to can be passed in instead.
    :param file_type_hint: Normally the file type is derived from the file extension. If the file extension is not
        clear or misleading, then this hint defines how it is tried to load it, e.g. ".json" for a json file.
        Supported formats so far are: *.json
        Default: None
    :param encoding: The encoding used to read the file. Defaults to 'ascii'.
    :returns :class:`.MapInfo` object containing loaded data.
    """
    # TODO: check file extension first
    # TODO: warn if file_type_hint and file extension differ (if both are provided)?
    # TODO: check file_type_hint
    # TODO: tmx facade should be instantiated here in the tmx path and passed along as map_data with index access
    file_type_hint = _get_file_type_hint(file_path, file_type_hint)
    s = file_like_object.read()
    return load_map_from_json_string(s, file_path, file_type_hint, encoding, load_visible_only)


def _get_file_type_hint(file_path, file_type_hint):
    if file_path and os.path.isfile(file_path):
        ext = os.path.splitext(file_path)[1]
        if not ext and not file_type_hint:
            raise MissingFileTypeException("Provide a file with an extension or a file_type_hint.")

        if not file_type_hint:
            file_type_hint = ext
    return file_type_hint


def load_map_from_data(map_data, file_path, load_visible_only=False):
    """load map from data

    Data is assumed to have been loaded from a Tiled map file, or constructed in a compatible manner.

    The decoder supports Tiled's zlib compression and base64 encoding.

    f = open('myMap.json', 'rb')
    json_map_data = json.load(f)
    map_info = load_map_from_json_data(json_map_data)

    :param file_path: the relative path to the map. Used to compute :class:`.TilesetInfo.image_path_rel_to_cwd`,
        otherwise None
    :param map_data: data from json.load()
    :return: :class:`.MapInfo`
    :raises: :class:`.VersionException` if the version can't be loaded
    """
    map_version = map_data["version"]  # this has to be the same for all versions!?
    if map_version == 1.0:
        return _load_version_1_map(map_data, file_path, load_visible_only)

    raise VersionException("unsupported map version {0}".format(map_version))


def _process_image_layer(json_layer, file_path):
    layer_type = json_layer["type"]
    if layer_type != IMAGE_LAYER_TYPE:
        raise InternalError("wrong layer type: should be {0} but is {1}".format(IMAGE_LAYER_TYPE, layer_type))
    # read data
    width = json_layer["width"]
    height = json_layer["height"]
    name = json_layer["name"]
    opacity = json_layer["opacity"]
    visible = json_layer["visible"]
    # optional
    layer_pixel_offset_x = json_layer.get("x", 0)
    layer_pixel_offset_y = json_layer.get("y", 0)
    layer_properties = json_layer.get("properties", {})
    image_path_relative_to_map = os.path.normpath(json_layer.get("image", 0))

    image_path_rel_to_cwd = _get_path_relative_to_cwd(file_path, image_path_relative_to_map)

    layer = ImageLayerInfo(name, layer_pixel_offset_x, layer_pixel_offset_y, width, height, visible, opacity,
                           layer_properties, image_path_relative_to_map, image_path_rel_to_cwd)
    return layer


def rotate_point(px, py, angle_in_deg, anchor_x=0, anchor_y=0, offset_x=0, offset_y=0):
    """
    Rotate a point around the anchor point about angle and add an offset.

    :param px: point x coordinate to rotate.
    :param py: point y coordinate to rotate.
    :param angle_in_deg: angle to rotate about.
    :param anchor_x: the anchor x coordinate to rotate around.
    :param anchor_y: the anchor y coordinate to rotate around.
    :param offset_x: the x offset to move the result.
    :param offset_y: the y offset to move the result.
    :return: transformed point, rotated about angle around anchor point and moved by offset.
    """
    _px = px - anchor_x
    _py = py - anchor_y
    rad_angle = math.radians(-angle_in_deg)
    cs = math.cos(rad_angle)
    si = math.sin(rad_angle)
    return cs * _px + si * _py + anchor_x + offset_x, -si * _px + cs * _py + anchor_y + offset_y


def _transform_points(points, angle_in_deg, anchor_x=0, anchor_y=0, offset_x=0, offset_y=0):
    """
    Transforms a list of points using the :function:`.rotate_point` function.

    :param points: The points to transform as a list of tuples, e.g. [(x1, y1), (x2, y2), ...].
    :param angle_in_deg: angle to rotate about.
    :param anchor_x: the anchor x coordinate to rotate around.
    :param anchor_y: the anchor y coordinate to rotate around.
    :param offset_x: the x offset to move the result.
    :param offset_y: the y offset to move the result.
    :return: List of transformed points.
    """
    # return [rotate_point(_px, _py, angle_in_deg, anchor_x, anchor_y, offset_x, offset_y) for _px, _py in points]
    _transformed = []
    _min_x = _min_y = sys.maxsize
    _max_x = _max_y = -sys.maxsize
    for _px, _py in points:
        _tx, _ty = rotate_point(_px, _py, angle_in_deg, anchor_x, anchor_y, offset_x, offset_y)
        _transformed.append((_tx, _ty))
        if _tx < _min_x:
            _min_x = _tx
        if _ty < _min_y:
            _min_y = _ty
        if _tx > _max_x:
            _max_x = _tx
        if _ty > _max_y:
            _max_y = _ty

    return _transformed, (_min_x, _min_y, _max_x - _min_x, _max_y - _min_y)


def _process_object_layer(json_layer, tiles_info):
    layer_type = json_layer["type"]
    if layer_type != OBJECT_LAYER_TYPE:
        raise InternalError("wrong layer type: should be {0} but is {1}".format(OBJECT_LAYER_TYPE, layer_type))
    # read data
    width = json_layer.get("width", -1)
    height = json_layer.get("height", -1)
    name = json_layer["name"]
    opacity = json_layer["opacity"]
    visible = json_layer["visible"]
    # noinspection SpellCheckingInspection
    draw_order = json_layer["draworder"]
    # optional
    # noinspection SpellCheckingInspection
    layer_pixel_offset_x = json_layer.get("offsetx", 0)
    # noinspection SpellCheckingInspection
    layer_pixel_offset_y = json_layer.get("offsety", 0)
    layer_properties = json_layer.get("properties", {})
    layer_tile_offset_x = json_layer.get("x", 0)
    layer_tile_offset_y = json_layer.get("y", 0)

    objects = []
    for obj in json_layer.get("objects", []):
        if "ellipse" in obj:
            r = ObjectEllipseInfo(obj["x"], obj["y"], obj["width"], obj["height"], obj["rotation"], obj["id"],
                                  obj["name"], obj.get("properties", {}), obj["visible"], obj["type"], obj["ellipse"])
            objects.append(r)
        elif "polygon" in obj:
            points = [(_p["x"], _p["y"]) for _p in obj["polygon"]]
            r = ObjectPolygonInfo(obj["x"], obj["y"], obj["width"], obj["height"], obj["rotation"], obj["id"],
                                  obj["name"], obj.get("properties", {}), obj["visible"], obj["type"], points)
            objects.append(r)
        elif "polyline" in obj:
            points = [(_p["x"], _p["y"]) for _p in obj["polyline"]]
            r = ObjectPolylineInfo(obj["x"], obj["y"], obj["width"], obj["height"], obj["rotation"], obj["id"],
                                   obj["name"], obj.get("properties", {}), obj["visible"], obj["type"], points)
            objects.append(r)
        elif "gid" in obj:
            gid = obj["gid"]
            tile_info = tiles_info[gid]
            obj["type"] = obj["type"] if obj["type"] != "" else tile_info.type  # todo do it for all types?
            r = ObjectTileInfo(obj["x"], obj["y"], obj["width"], obj["height"], obj["rotation"], obj["id"], obj["name"],
                               obj.get("properties", {}), obj["visible"], obj["type"], gid, tile_info)
            objects.append(r)
        else:
            r = ObjectRectangleInfo(obj["x"], obj["y"], obj["width"], obj["height"], obj["rotation"], obj["id"],
                                    obj["name"], obj.get("properties", {}), obj["visible"], obj["type"])
            objects.append(r)

    # calculate bounding box  # todo fix (this isn't a bounding box!)
    if width == -1:
        for obj in objects:
            if obj.width > width:
                width = obj.width + obj.x
    if height == -1:
        for obj in objects:
            if obj.height > height:
                height = obj.height + obj.y

    layer = ObjectLayerInfo(name, layer_pixel_offset_x, layer_pixel_offset_y, width, height, visible, opacity,
                            layer_properties, layer_tile_offset_x, layer_tile_offset_y, draw_order, objects)
    return layer


def _load_version_1_map(map_data, map_path, load_visible_only):
    tiles_info = _load_tiles_info_from_tilesets(map_data, map_path)  # {gid: TileInfo}
    # noinspection SpellCheckingInspection
    tile_w = map_data["tilewidth"]  # TODO rename to map_tile_w and rename down the call stack too
    # noinspection SpellCheckingInspection
    tile_h = map_data["tileheight"]  # TODO rename to map_tile_h and rename down the call stack too
    # TODO: add missing attributes and pass them down
    # "next object id":1,
    # "orientation":"orthogonal",
    # TODO: sort the tile-layer data according to this already? or just make an sort key method available?
    # "render order":"right-down",
    converted_layers = []
    json_layers = map_data.get("layers", None)
    # FIXME: in pytmxloader repo; the json format may have changed?
    # map_properties = map_data.get("properties", {})
    map_properties = {}
    for k, v in map_data.items():
        if k != "layers":
            map_properties[k] = map_data[k]
    # FIXME: end --------------------------------------------------
    if json_layers:
        for json_layer in json_layers:
            layer_type = json_layer["type"]
            layer = None
            # noinspection SpellCheckingInspection
            if layer_type == TILE_LAYER_TYPE:
                layer = _process_tile_layer(json_layer, tile_w, tile_h, tiles_info)
            elif layer_type == IMAGE_LAYER_TYPE:
                layer = _process_image_layer(json_layer, map_path)
            elif layer_type == OBJECT_LAYER_TYPE:
                layer = _process_object_layer(json_layer, tiles_info)
            else:
                # TODO: replace all print() with logger!
                print("processing for layer type {0} is not implemented yet!".format(layer_type))
            if layer:
                if load_visible_only and not layer.visible:
                    continue
                converted_layers.append(layer)
    else:
        print("layers None")
    return MapInfo(converted_layers, tiles_info, map_properties)


def _process_tile_layer(json_layer, tile_w, tile_h, tiles_info):
    layer_type = json_layer["type"]
    if layer_type != TILE_LAYER_TYPE:
        raise InternalError("wrong layer type: should be {0} but is {1}".format(TILE_LAYER_TYPE, layer_type))

    # read data
    width = json_layer["width"]
    height = json_layer["height"]
    name = json_layer["name"]
    # print('layer: {}'.format(name))  # TODO: use logger!!
    opacity = json_layer["opacity"]
    visible = json_layer["visible"]
    binary_data = json_layer["data"]
    # optional
    # noinspection SpellCheckingInspection
    layer_pixel_offset_x = json_layer.get("offsetx", 0)
    # noinspection SpellCheckingInspection
    layer_pixel_offset_y = json_layer.get("offsety", 0)
    encoding = json_layer.get("encoding", "")
    compression = json_layer.get("compression", "")
    layer_properties = json_layer.get("properties", {})
    layer_offset_x_in_tiles = json_layer.get("x", 0)
    layer_offset_y_in_tiles = json_layer.get("y", 0)

    # process and save data
    decoded_data = _decode_layer_data(binary_data, width, height, encoding, compression)
    layer_info_tiles = _build_tile_layer_tile_info_tiles(decoded_data, width, height, tile_w, tile_h, tiles_info,
                                                         layer_pixel_offset_x, layer_pixel_offset_y,
                                                         layer_offset_x_in_tiles, layer_offset_y_in_tiles)
    layer = TileLayerInfo(name, layer_pixel_offset_x, layer_pixel_offset_y, width, height, tile_w, tile_h, visible,
                          opacity,
                          layer_info_tiles, layer_properties, layer_offset_x_in_tiles, layer_offset_y_in_tiles)
    return layer


def _build_tile_layer_tile_info_tiles(json_data, width, height, layer_tile_w, layer_tile_h, tiles_info,
                                      layer_offset_x_pixels, layer_offset_y_pixels, layer_offset_x_in_tiles,
                                      layer_offset_y_in_tiles):
    data = []
    for y in range(height):
        data.append([])
        for x in range(width):
            gid = json_data[y * width + x]  # TODO: if that would be a generator, how to use it here? -> changes loop!
            # data[y].append(gid)
            if gid == 0:
                data[y].append(None)
                continue
            if gid & _ALL_FLIP_BITS != 0:
                # modified tile detected, add it if not already present
                if gid not in tiles_info:
                    _tile_info = _get_rotated_or_flipped_tile(gid, tiles_info)
                    tiles_info[gid] = _tile_info  # add the rotated/flipped tile as a new tile with its gid
            tile_info = tiles_info[gid]
            topleft_offset_y = -tile_info.tileset.tile_height + layer_tile_h
            topleft_offset_x = 0
            # TODO: this calculations depend on the map type: orthogonal is different than staggered, etc.
            tile_off_x = layer_offset_x_in_tiles * layer_tile_w
            tile_x = x * layer_tile_w + tile_info.tileset.pixel_offset_x + layer_offset_x_pixels + tile_off_x
            tile_off_y = layer_offset_y_in_tiles * layer_tile_h
            tile_y = y * layer_tile_h + tile_info.tileset.pixel_offset_y + layer_offset_y_pixels + tile_off_y
            data[y].append(TileLayerTileInfo(tile_x, tile_y, tile_info, topleft_offset_x, topleft_offset_y))
    return data


# noinspection SpellCheckingInspection
def _get_tiles_from_tsx(tile_info_dict, map_file_path, first_gid, source):
    source_rel_to_cwd = _get_path_relative_to_cwd(map_file_path, source)

    # todo AFTER_PYWEEK cache tsx file content?

    if source_rel_to_cwd:
        tree = ElementTree()
        tree.parse(source_rel_to_cwd)

        tileset = {}
        root_node = tree.getroot()
        root_node_attrib = root_node.attrib
        tileset["tilecount"] = int(root_node_attrib["tilecount"])
        tileset["margin"] = int(root_node_attrib["margin"]) if "margin" in root_node_attrib else 0
        tileset["spacing"] = int(root_node_attrib["spacing"]) if "spacing" in root_node_attrib else 0
        tileset["properties"] = {}
        properties_node = root_node.find("properties")
        if properties_node is not None:
            tileset["properties"] = _get_properties_from_property_node(properties_node)

        tileoffset_node = tree.find("tileoffset")
        tileset["x"] = 0 if tileoffset_node is None else int(tileoffset_node.attrib["x"])
        tileset["y"] = 0 if tileoffset_node is None else int(tileoffset_node.attrib["y"])
        tile_width = int(root_node_attrib["tilewidth"])
        tile_height = int(root_node_attrib["tileheight"])
        name = root_node_attrib["name"]

        tiles_properties = {}  # {id : {propname: value}}
        tile_nodes = root_node.findall("tile")
        tileset["tiles"] = {}
        for tile_node in tile_nodes:
            tile_node_id = tile_node.attrib["id"]
            tile_node_type = tile_node.get("type", "")
            tile_node_properties_list = tile_node.find("properties")
            tiles_properties[tile_node_id] = {}
            if tile_node_properties_list is not None:
                tiles_properties[tile_node_id] = _get_properties_from_property_node(tile_node_properties_list)
            tileset["tiles"][int(tile_node_id)] = {
                "probability": float(tile_node.attrib["probability"]) if "probability" in tile_node.attrib else 1.0}
            tileset["tiles"][int(tile_node_id)]["type"] = tile_node_type

            animation = None
            anim_node = tile_node.find("animation")
            if anim_node is not None:
                animation = []
                frames = anim_node.findall("frame")
                for frame in frames:
                    animation.append(
                        {"tileid": first_gid + int(frame.attrib["tileid"]), "duration": int(frame.attrib["duration"])})

            tileset["tiles"][int(tile_node_id)]["animation"] = animation

            tile_image_node = tile_node.find("image")
            if tile_image_node is not None:
                tileset["tiles"][int(tile_node_id)]["image"] = tile_image_node.attrib["source"]
                tileset["tiles"][int(tile_node_id)]["width"] = int(tile_image_node.attrib["width"])
                tileset["tiles"][int(tile_node_id)]["height"] = int(tile_image_node.attrib["height"])

        tileset["tileproperties"] = tiles_properties

        image_node = tree.find("image")
        if image_node is None:
            # this tsx file is an image collection
            _get_tiles_from_collection_of_images(map_file_path, first_gid, name, tile_height,
                                                 tile_info_dict, tile_width, tileset, tiles_properties)

        else:
            # this tsx file is a tileset
            image_path_relative_to_map = image_node.attrib["source"]
            tileset["imagewidth"] = int(image_node.attrib["width"])
            tileset["imageheight"] = int(image_node.attrib["height"])
            if "trans" in image_node.attrib:
                tileset["transparentcolor"] = image_node.attrib["trans"]

            _get_tiles_from_tileset(map_file_path, first_gid, image_path_relative_to_map, name, tile_height,
                                    tile_info_dict, tile_width, tileset, tiles_properties)


def _get_properties_from_property_node(properties_node):
    properties = {}
    property_node_list = properties_node.findall("property")
    for prop in property_node_list:
        properties[prop.attrib["name"]] = prop.attrib["value"]
    return properties


def _load_tiles_info_from_tilesets(map_data, map_file_path):
    tilesets = map_data.get("tilesets", None)

    if not tilesets:
        print("no tilesets present")
        return {}

    tile_info_dict = {}  # {gid: TileInfo}
    for tileset in tilesets:
        # noinspection SpellCheckingInspection
        first_gid = tileset["firstgid"]
        source = tileset.get("source", None)
        if source:
            # loading from a tsx file
            _get_tiles_from_tsx(tile_info_dict, map_file_path, first_gid, source)
        else:
            # tileset of image collection loading
            # noinspection SpellCheckingInspection
            tile_height = tileset["tileheight"]
            # noinspection SpellCheckingInspection
            tile_width = tileset["tilewidth"]
            name = tileset["name"]
            # noinspection SpellCheckingInspection
            tiles_properties = tileset.get("tileproperties", {})
            # TODO: check if its an image with properties instead of a filename!
            image_path_relative_to_map = tileset.get("image", None)  # TODO: check here already if the files exists??
            if image_path_relative_to_map:
                _get_tiles_from_tileset(map_file_path, first_gid, image_path_relative_to_map, name, tile_height,
                                        tile_info_dict, tile_width, tileset, tiles_properties)
            else:
                _get_tiles_from_collection_of_images(map_file_path, first_gid, name, tile_height,
                                                     tile_info_dict, tile_width, tileset, tiles_properties)
    return tile_info_dict


def _get_tiles_from_collection_of_images(file_path, first_gid, name, tile_height, tile_info_dict, tile_width, tileset,
                                         tiles_properties):
    _tiles = tileset["tiles"]  # {id: image_path}
    # noinspection SpellCheckingInspection

    for idx, tile_data in _tiles.items():
        gid = first_gid + int(idx)
        image_path_relative_to_map = os.path.normpath(tile_data["image"])
        tile_width = tile_data["width"] if "width" in tile_data else tile_width
        tile_height = tile_data["height"] if "height" in tile_data else tile_height
        tile_type = tile_data["type"]
        image_rel_to_cur = _get_path_relative_to_cwd(file_path, image_path_relative_to_map)
        tile_set_info = _create_tileset_info(gid, image_path_relative_to_map, image_rel_to_cur, name, tile_width,
                                             tile_height, tileset)
        properties_of_tile = tiles_properties.get(str(idx), {})
        tile_info_dict[gid] = TileInfo(gid, tile_set_info, 0, 0, properties_of_tile, tile_type=tile_type)
    _get_animation_frames(first_gid, tile_info_dict, tileset)


# noinspection SpellCheckingInspection
def _get_tiles_from_tileset(file_path, first_gid, image_path_relative_to_map, name, tile_height, tile_info_dict,
                            tile_width, tileset, tiles_properties):
    image_rel_to_cur = _get_path_relative_to_cwd(file_path, image_path_relative_to_map)

    tile_set_info = _create_tileset_info(first_gid, image_path_relative_to_map, image_rel_to_cur, name, tile_width,
                                         tile_height, tileset)
    tile_count = tileset["tilecount"]
    image_width = tileset["imagewidth"]
    # image_height = tileset["imageheight"]
    margin = tileset["margin"]
    spacing = tileset["spacing"]
    tile_width_with_space = tile_width + spacing
    tile_height_with_space = tile_height + spacing
    row_count = image_width // tile_width_with_space
    for idx in range(tile_count):
        spritesheet_x = margin + (idx % row_count) * tile_width_with_space
        spritesheet_y = margin + (idx // row_count) * tile_height_with_space
        gid = first_gid + idx
        properties_of_tile = tiles_properties.get(str(idx), {})
        tile = tileset["tiles"].get(idx, None)
        tile_type = tile.get("type", None) if tile else None
        tile_info_dict[gid] = TileInfo(gid, tile_set_info, spritesheet_x, spritesheet_y, properties_of_tile, tile_type=tile_type)

    # update data from tiles after loading them since they may reference the loaded tile data
    _get_animation_frames(first_gid, tile_info_dict, tileset)


def _get_animation_frames(first_gid, tile_info_dict, tileset):
    tiles = tileset.get("tiles", {})
    for idx, tile_values in tiles.items():
        key = first_gid + int(idx)
        tile_info_dict[key].probability = tile_values.get("probability", 1.0)
        animation = tile_values.get("animation", None)
        if animation is not None:
            frames = []
            for a in animation:
                # noinspection SpellCheckingInspection
                _tile_id = a["tileid"]
                frames.append(AnimationFrameInfo(tile_info_dict[_tile_id], a["duration"]))
            tile_info_dict[key].animation = frames


def _create_tileset_info(first_gid, image_path_relative_to_map, image_rel_to_cur, name, tile_width, tile_height,
                         tileset):
    tileset_properties = tileset.get("properties", {})
    # noinspection SpellCheckingInspection
    transparent_color = tileset.get("transparentcolor", None)  # TODO: define format, convert to tuple?
    # noinspection SpellCheckingInspection
    tile_offset = tileset.get("tileoffset", {})
    pixel_offset_x = tile_offset.get("x", 0)
    pixel_offset_y = tile_offset.get("y", 0)
    tile_set_info = TilesetInfo(name, tile_width, tile_height, tileset_properties, image_path_relative_to_map,
                                image_rel_to_cur, first_gid, transparent_color, pixel_offset_x, pixel_offset_y)
    return tile_set_info


def _get_path_relative_to_cwd(file_path, path_relative_to_file):
    if file_path:
        directory_name = file_path if os.path.isdir(file_path) else os.path.dirname(file_path)
        _image_rel = os.path.join(directory_name, path_relative_to_file)
        image_rel_to_cur = os.path.normpath(os.path.relpath(_image_rel))
        return image_rel_to_cur
    return None


def _get_rotated_or_flipped_tile(gid, tiles_info):
    flag_key = gid & _ALL_FLIP_BITS  # clear all flags except the flip bits
    rot, flip_v, flip_h = _flag_to_rot_flips[flag_key]
    actual_gid = gid & ~_ALL_FLIP_BITS  # clear flip bits to get the gid of the used tile
    source_tile = tiles_info[actual_gid]
    tile_info = TileInfo(gid, source_tile.tileset, source_tile.spritesheet_x,
                    source_tile.spritesheet_y, source_tile.properties, rot, flip_h, flip_v, source_tile.probability,
                    source_tile.animation, tile_type = source_tile.type)
    return tile_info


def _decode_layer_data(json_data, width, height, encoding, compression, string_encoding="latin-1"):
    if encoding == "base64":
        decoded_data = base64.b64decode(json_data.encode(string_encoding))
        if compression == "zlib":
            packed_data = zlib.decompress(decoded_data)
        elif compression == "gzip":
            if sys.version_info > (2,):
                compressed_stream = BytesIO(decoded_data)
            else:
                compressed_stream = StringIO(decoded_data.decode(string_encoding))
            with gzip.GzipFile(fileobj=compressed_stream) as gz_file_stream:
                packed_data = gz_file_stream.read()
                gz_file_stream.close()
        else:
            packed_data = decoded_data

        gid_list = _decode_packed_array(packed_data, width, height)
    else:
        gid_list = json_data

    return gid_list


def _decode_packed_array(content, width, height):
    format_string = "<" + "I" * width * height
    calculated_size = struct.calcsize(format_string)
    assert calculated_size == len(content), "{0} != {1}".format(calculated_size, len(content))
    return struct.unpack(format_string, content)  # maybe use the iteration version for time slicing


# TODO: check that x, y, width and height are set for all objects
class ObjectBaseInfo(EquatableMixin):
    def __init__(self, x, y, width, height, rotation, object_id, name, properties, visible, object_type):
        """
        The base object info object. It holds the common attributes of the different objects of the object layer.
        It holds an attribute called 'pixel_rect' which is the axis aligned bounding box (aabb) of the transformed
        points hold in the attribute 'pixel_points'. It's a tuple like (x, y, w, h)

        :param x: The x coordinate of the object.
        :param y: The y coordinate of the object.
        :param width: The width of the object.
        :param height: The height of the object.
        :param rotation: The rotation of the object.
        :param object_id: The object id. Unique for each object.
        :param name: The name of the object.
        :param properties: The properties of this object as a dict like {"name": "value"}
        :param visible: Visibility flag.
        :param object_type: This is the string that is provided as type.
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rotation = rotation
        self.id = object_id
        self.name = name
        self.properties = properties
        self.visible = visible
        self.type = object_type
        self.pixel_rect = (x, y, width, height)

    def __eq__(self, other):
        if isinstance(other, ObjectBaseInfo):
            return self.x == other.x and \
                   self.y == other.y and \
                   self.width == other.width and \
                   self.height == other.height and \
                   self.rotation == other.rotation and \
                   self.id == other.id and \
                   self.name == other.name and \
                   self.properties == other.properties and \
                   self.visible == other.visible and \
                   self.type == other.type
        return NotImplemented


class ObjectRectangleInfo(ObjectBaseInfo):
    def __init__(self, x, y, width, height, rotation, object_id, name, properties, visible, object_type):
        """
        The rectangle object. Defined by x, y, width, height and rotation. The anchor point for the rotation is
        the topleft corner (x, y). For convenient rendering there is the pixel_points attribute.
        This contains transformed (moved and rotated) points.

        For other arguments see :class:`.ObjectBaseInfo`.
        """
        ObjectBaseInfo.__init__(self, x, y, width, height, rotation, object_id, name, properties, visible, object_type)

        _points = [(x, y), (x + width, y), (x + width, y + height), (x, y + height)]
        self.pixel_points, self.pixel_rect = _transform_points(_points, self.rotation, x, y)

    def __eq__(self, other):
        if isinstance(other, ObjectRectangleInfo):
            return ObjectBaseInfo.__eq__(self, other) and \
                   self.pixel_rect == other.pixel_rect and \
                   self.pixel_points == other.pixel_points
        return NotImplemented


class ObjectEllipseInfo(ObjectBaseInfo):
    def __init__(self, x, y, width, height, rotation, object_id, name, properties, visible, object_type, ellipse):
        """
        The ellipse object. It is defined by its width and height and the anchor point is topleft at (x, y).
        For other arguments see :class:`.ObjectBaseInfo`.

        :param ellipse: bool, if it is an ellipse it is set to True, not sure in which cases it would be False!
        """
        ObjectBaseInfo.__init__(self, x, y, width, height, rotation, object_id, name, properties, visible, object_type)
        self.ellipse = ellipse
        _points = [(x, y), (x + width, y), (x + width, y + height), (x, y + height)]
        self.pixel_points, self.pixel_rect = _transform_points(_points, self.rotation, x, y)

    def __eq__(self, other):
        if isinstance(other, ObjectEllipseInfo):
            return ObjectBaseInfo.__eq__(self, other) and self.ellipse == other.ellipse and \
                   self.pixel_rect == other.pixel_rect and \
                   self.pixel_points == other.pixel_points
        return NotImplemented


class ObjectPolygonInfo(ObjectBaseInfo):
    def __init__(self, x, y, width, height, rotation, object_id, name, properties, visible, object_type, points):
        """
        The polygon object. It defines a polygon. For convenient rendering there is the pixel_points attribute.
        This contains transformed (moved and rotated) points.
        For other arguments see :class:`.ObjectBaseInfo`.

        :param points: A list of [(px, py), ...] points. They are not transformed and relative to (x, y)
        """
        ObjectBaseInfo.__init__(self, x, y, width, height, rotation, object_id, name, properties, visible, object_type)
        self.points = points
        self.pixel_points, self.pixel_rect = _transform_points(self.points, self.rotation, offset_x=self.x,
                                                               offset_y=self.y)

    def __eq__(self, other):
        if isinstance(other, ObjectPolygonInfo):
            return ObjectBaseInfo.__eq__(self, other) and self.points == other.points and \
                   self.pixel_rect == other.pixel_rect and \
                   self.pixel_points == other.pixel_points
        return NotImplemented


class ObjectPolylineInfo(ObjectBaseInfo):
    def __init__(self, x, y, width, height, rotation, object_id, name, properties, visible, object_type, points):
        """
        The poly line object. It defines a line. For convenient rendering there is the pixel_points attribute.
        This contains transformed (moved and rotated) points.
        For other arguments see :class:`.ObjectBaseInfo`.

        :param points: A list of [(px, py), ...] points. They are not transformed and relative to (x, y)
        """
        ObjectBaseInfo.__init__(self, x, y, width, height, rotation, object_id, name, properties, visible, object_type)
        self.points = points
        self.pixel_points, self.pixel_rect = _transform_points(self.points, self.rotation, offset_x=self.x,
                                                               offset_y=self.y)

    def __eq__(self, other):
        if isinstance(other, ObjectPolylineInfo):
            return ObjectBaseInfo.__eq__(self, other) and self.points == other.points and \
                   self.pixel_rect == other.pixel_rect and \
                   self.pixel_points == other.pixel_points
        return NotImplemented


class ObjectTileInfo(ObjectBaseInfo):
    def __init__(self, x, y, width, height, rotation, object_id, name, properties, visible, object_type, gid,
                 tile_info):
        """
        The tile object. It defines a tile.
        For other arguments see :class:`.ObjectBaseInfo`.

        :param gid: The gid from a tile in a tileset. See :class:`.MapInfo`.
        :param tile_info: The reference to an instance of :class:`.TileInfo`.
        """
        ObjectBaseInfo.__init__(self, x, y, width, height, rotation, object_id, name, properties, visible, object_type)
        self.gid = gid
        self.tile_info = tile_info
        # TODO: maybe x, y should be topleft as in the other objects
        # TODO: depending on draw type this has to be done differently
        # from the docs:
        # The image alignment currently depends on the map orientation. In orthogonal orientation it's aligned to
        # the bottom-left while in isometric it's aligned to the bottom-center.
        #
        # tile object have bottom left as anchor points! TODO: does this depend on draw type?
        _points = [(x, y), (x, y - height), (x + width, y - height), (x + width, y)]
        self.pixel_points, self.pixel_rect = _transform_points(_points, self.rotation, x, y)

    def __eq__(self, other):
        if isinstance(other, ObjectTileInfo):
            return ObjectBaseInfo.__eq__(self, other) and self.gid == other.gid and self.tile_info == other.tile_info \
                   and self.pixel_rect == other.pixel_rect
        return NotImplemented
