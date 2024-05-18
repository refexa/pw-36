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

.. versionchanged:: 0.0.0.0
    initial version

"""
import xml.sax
import logging
import os

__version__ = '4.0.0.0'

# for easy comparison as in sys.version_info but digits only
__version_info__ = tuple([int(d) for d in __version__.split('.')])

__author__ = 'DR0ID'
__email__ = 'dr0iddr0id [at] googlemail [dot] com'
__copyright__ = "DR0ID @ 2014"
__credits__ = ["DR0ID"]  # list of contributors
__maintainer__ = "DR0ID"
__license__ = "New BSD license"


# __all__ = []  # list of public visible parts of this module


class Orientation(object):
    orthogonal = "orthogonal"
    hexagonal = "hexagonal"  # TODO: verify?
    isometric = "isometric"  # TODO: isometric and staggered the same?
    staggered = "staggered"


class LayerType(object):
    TileLayer = 0  # use strings here?
    ObjectGroup = 1
    Image = 2


class ObjectShape(object):
    Rectangle = 0
    Ellipse = 1
    Polygon = 2
    Polyline = 3
    Image = 4


class MapInfo(object):
    def __init__(self):
        self.g_images = {}  # {gid : (offset_x, offset_y, image)}
        self.g_tiles = {}  # {gid : TileInfo}

        # may contain these
        self.properties = {}  # {string : string}
        self.tilesets = []  # [TilesetInfo]
        self.layers = []  # [LayerInfo] order is back to front!
        self.object_groups = []
        self.image_layers = []

        # attributes
        self.version = 1.0
        self.orientation = Orientation.orthogonal
        self.width = 0  # number of tiles
        self.height = 0  # number of tiles
        self.tile_width = 0  # width of a tile in pixels
        self.tile_height = 0  # height of a tile in pixels
        self.background_color = (0, 0, 0)  # since 0.9.0


class TilesetInfo(object):
    def __init__(self):
        self.first_gid = 0  # starting gid of this tileset
        self.source = ""  # path to tsx file

        self.name = 0
        self.tile_width = 0
        self.tile_height = 0
        self.spacing = 0  # pixels between images
        self.margin = 0  # pixels along the border

        self.tile_offset_x = 0  # in pixels
        self.tile_offset_y = 0  # in pixels, positive is down

        self.properties = {}  # {string : string}
        self.images = []  # ImageInfo
        self.terrain_types = []
        self.tiles = []  # TileInfo

        self.g_tiles = {}  # {gid : TileInfo}  <-- in MapInfo


# noinspection SpellCheckingInspection
class ImageInfo(object):
    def __init__(self):
        self.format = "png"  # format can be either of these:
        # BMP	Windows Bitmap
        # GIF	Graphic Interchange Format (optional)
        # JPG	Joint Photographic Experts Group
        # JPEG	Joint Photographic Experts Group
        # MNG	Multiple-image Network Graphics
        # PNG	Portable Network Graphics
        # PBM	Portable Bitmap
        # PGM	Portable Graymap
        # PPM	Portable Pixmap
        # TIFF	Tagged Image File Format
        # XBM	X11 Bitmap
        # XPM	X11 Pixmap
        # SVG	Scalable Vector Graphics
        # TGA	Targa Image Format
        self.id = 0  # deprecated
        self.source = ""  # path to the image
        self.trans = "FF00FF"  # transparent color, colorkey
        self.width = 0  # optional, in pixels
        self.height = 0  # optional, in pixels
        self.data = ""  # embedded image
        self.data_encoding = "base64"


class TerrainInfo(object):
    def __init__(self):
        self.name = ""
        self.tile = 0  # local tile-id of the tile that represents the terrain visually


class TileInfo(object):
    def __init__(self):
        self.id = 0  # local id within tileset
        self.terrain = "1,2,3,4"  # optional terrain type of each corner as index of terrain types array, tl, tr, bl, br
        self.probability = 0.5  # optional, a percentage indicating that this is chosen while editing in terrain tool
        self.properties = {}  # {string : string}
        self.images = []  # optional [ImageInfo]

        # self.gid = 0  # global id
        # self.rect = (0, 0, 32, 32)  # rect as (x, y, w, h) tuple
        # self.flip_x = False  # flipped in x direction
        # self.flip_y = False  # flipped in y direction
        # self.flip_d = False  # flipped diagonally  <-- maybe better to provide rotation angle?
        # # shared with other TileInfo
        # self.tileset_properties = {}  # {string : string}, same for all image of same tileset, TilesetInfo.properties


class LayerInfo(object):
    def __init__(self):
        self.name = ""  # name of layer
        self.pos_x = 0  # in tiles
        self.pos_y = 0  # in tiles
        self.width = 0  # in num tiles
        self.height = 0  # in num tiles
        self.opacity = 1  # from 0 to 1, default 1
        self.visible = 0  # 0, 1, default 1
        self.properties = {}  # {string : string}
        self.data = ""  #
        self.data_encoding = "base64"  # or csv
        self.data_compression = "gzip"  # or zlib
        # noinspection SpellCheckingInspection
        self.layer_tiles_gid = []  # the gids from the tile element

        self.type = LayerType.TileLayer


class ObjectGroup(object):
    def __init__(self):
        self.name = ""
        self.color = "FF00FF"  # color to display the objects of this group
        self.x = 0  # the x coordinate in tiles, always 0 in TiledQT
        self.y = 0  # the y coordinate in tiles, always 0 in TiledQT
        self.width = 0  # in tiles
        self.height = 0  # in tiles
        self.opacity = 1  # from 0 to 1
        self.visible = 1  # 0 or 1

        self.type = LayerType.ObjectGroup

        self.properties = {}  # {string : string}
        self.objects = []  # [ObjectInfo]


class ObjectInfo(object):
    def __init__(self):
        self.name = ""
        self.type = ""  # type of object, arbitrary string
        self.pos_x = 0  # x coord of object in pixels, bottom-left for orthogonal, bottom center for isometric
        self.pos_y = 0  # y coord of object in pixels, bottom-left for orthogonal, bottom center for isometric
        self.width = 0  # width in pixels, default 0, ignored if gid is set
        self.height = 0  # height in pixels, default 0, ignored if gid is set
        self.rotation = 0  # rotation of object in degrees clockwise
        self.gid = 0  # optional, reference to a tile
        self.visible = 1  # 0 or 1
        self.properties = {}
        self.points = []  # list of points used by polygon or polyline, depending on shape
        self.gid = 0  # only set if shape is Image, referencing a tile
        self.shape = ObjectShape.Rectangle
        self.type = ""  # type define in Edit/Preferences


class ImageLayer(object):
    def __init__(self):
        self.name = ""
        self.width = 0  # width in tiles
        self.height = 0  # height in tiles
        self.opacity = 1  # from 0 to 1
        self.visible = 1  # 0 or 1
        self.properties = {}
        self.image = []  # [ImageInfo]


# ===================================================================================

_ELEM_PROPERTIES = 'properties'

_ELEM_TILESET = 'tileset'

_ELEM_MAP = 'map'

_ELEM_TILESETS = 'tilesets'

_ELEM_IMAGE = 'image'

_ATTR_VALUE = 'value'

_ATTR_NAME = 'name'

_ELEM_PROPERTY = 'property'

# noinspection SpellCheckingInspection
_ATTR_IMAGE_HEIGHT = 'imageheight'

# noinspection SpellCheckingInspection
_ATTR_IMAGE_WIDTH = 'imagewidth'

_ATTR_SOURCE = 'source'

_ATTR_VERSION = 'version'

# noinspection SpellCheckingInspection
_ATTR_FIRST_GID = 'firstgid'

# noinspection SpellCheckingInspection
_ATTR_TILE_WIDTH = 'tilewidth'

# noinspection SpellCheckingInspection
_ATTR_TILE_HEIGHT = 'tileheight'

_ATTR_HEIGHT = 'height'

_ATTR_WIDTH = 'width'

_ATTR_TRANS = 'trans'

# noinspection SpellCheckingInspection
_ATTR_TRANSPARENT_COLOR = 'transparentcolor'

_ATTR_Y = 'y'

_ATTR_X = 'x'

# noinspection SpellCheckingInspection
_ELEM_TILE_OFFSET = 'tileoffset'

_ATTR_MARGIN = 'margin'

_ATTR_SPACING = 'spacing'

_ATTR_LAYERS = 'layers'

_type_converter_map = {_ATTR_WIDTH: int,
                       _ATTR_HEIGHT: int,
                       _ATTR_TILE_HEIGHT: int,
                       _ATTR_TILE_WIDTH: int,
                       _ATTR_FIRST_GID: int,
                       _ATTR_VERSION: lambda v: int(v.split('.')[0]),
                       _ATTR_MARGIN: int,
                       _ATTR_SPACING: int,
                       _ATTR_X: int,
                       _ATTR_Y: int,
                       _ATTR_TRANS: lambda v: v if v.startswith('#') else '#' + v}


def _no_conversion(x): return x


def _convert_type(key, value, default_conversion=_no_conversion):
    return _type_converter_map.get(key, default_conversion)(value)


def _set_attributes_to_dict(the_dictionary, attributes):
    for k, v in list(attributes.items()):
        the_dictionary[k] = _convert_type(k, v)


# noinspection PyClassicStyleClass
def _get_abs_path_of_relative_path(base_path, relative_path):
    if not os.path.isabs(relative_path):
        if os.path.isfile(base_path):
            base_path = os.path.dirname(base_path)
        relative_path = os.path.join(base_path, relative_path)
    return os.path.normpath(relative_path)


# noinspection PyClassicStyleClass
class Handler(xml.sax.ContentHandler):

    def __init__(self, logger):
        xml.sax.ContentHandler.__init__(self)
        self.file_name = None
        self.logger = logger
        self.stack = []
        self.map_as_json = None

    def parse_tsx_file(self, tsx_file_name):
        tsx_handler = Handler(self.logger)
        tsx_file_name = _get_abs_path_of_relative_path(self.file_name, tsx_file_name)
        tsx_handler.parse(tsx_file_name)
        tsx_tileset = tsx_handler.stack[-1]
        return tsx_tileset

    def startElement(self, name, attributes):
        self.logger.debug("startElement '%s': %s", name,
                          [(attr_name, attributes.getValue(attr_name)) for attr_name in attributes.getNames()])
        if name == _ELEM_MAP:
            self.stack.append({_ATTR_LAYERS: [], _ELEM_PROPERTIES: {}, _ELEM_TILESETS: []})
            _set_attributes_to_dict(self.stack[-1], attributes)
            return
        elif name == _ELEM_TILESET:
            self.stack.append({_ELEM_PROPERTIES: {}, _ATTR_SPACING: 0, _ATTR_MARGIN: 0})
            if _ATTR_SOURCE in attributes.getNames():
                # external tsx file
                tsx_file_name = attributes.getValue(_ATTR_SOURCE)

                tsx_tileset = self.parse_tsx_file(tsx_file_name)

                # TODO: is there a simpler way to get the relative path to tmx files?
                image_path_rel_to_tsx = tsx_tileset[_ELEM_IMAGE]
                tsx_file_name = _get_abs_path_of_relative_path(self.file_name, tsx_file_name)
                abs_tmx_path = os.path.dirname(os.path.abspath(self.file_name))
                image_path = _get_abs_path_of_relative_path(tsx_file_name, image_path_rel_to_tsx)
                rel_path = os.path.relpath(image_path, abs_tmx_path)
                rel_path = os.path.normpath(rel_path).replace(os.sep, "/")  # simple slash as separator!
                tsx_tileset[_ELEM_IMAGE] = rel_path

                self.stack[-1].update(tsx_tileset)
                self.stack[-1][_ATTR_FIRST_GID] = _convert_type(_ATTR_FIRST_GID, attributes.getValue(_ATTR_FIRST_GID))
            else:
                _set_attributes_to_dict(self.stack[-1], attributes)
            return
        elif name == _ELEM_PROPERTIES:
            properties = {}
            _set_attributes_to_dict(properties, attributes)
            self.stack.append(properties)
            return
        elif name == _ELEM_PROPERTY:
            parent_properties = self.stack[-1]
            parent_properties[attributes.getValue(_ATTR_NAME)] = attributes.getValue(_ATTR_VALUE)
            return
        elif name == _ELEM_IMAGE:
            parent_tileset = self.stack[-1]
            parent_tileset[_ELEM_IMAGE] = _convert_type(_ATTR_SOURCE, attributes.getValue(_ATTR_SOURCE))
            # optional, may not be present
            if _ATTR_WIDTH in attributes.getNames():
                parent_tileset[_ATTR_IMAGE_WIDTH] = _convert_type(_ATTR_WIDTH, attributes.getValue(_ATTR_WIDTH))
            if _ATTR_HEIGHT in attributes.getNames():
                parent_tileset[_ATTR_IMAGE_HEIGHT] = _convert_type(_ATTR_HEIGHT, attributes.getValue(_ATTR_HEIGHT))
            if _ATTR_TRANS in attributes.getNames():
                parent_tileset[_ATTR_TRANSPARENT_COLOR] = _convert_type(_ATTR_TRANS, attributes.getValue(_ATTR_TRANS))
            return
        elif name == _ELEM_TILE_OFFSET:
            self.stack.append({})
            _set_attributes_to_dict(self.stack[-1], attributes)
            return

        self.logger.warn("startElement '%s' was unhandled!", name)

    def endElement(self, name):
        self.logger.debug("endElement '%s'", name)
        if name == _ELEM_MAP:
            self.map_as_json = self.stack[-1]
            return
        elif name == _ELEM_TILESET:
            if len(self.stack) <= 1:
                # parsing tsx file, nothing to do
                pass
            else:
                tileset = self.stack.pop()
                self.stack[-1].get(_ELEM_TILESETS, []).append(tileset)
            return
        elif name == _ELEM_PROPERTIES:
            properties = self.stack.pop()
            self.stack[-1][_ELEM_PROPERTIES] = properties
            return
        elif name == _ELEM_PROPERTY:
            return
        elif name == _ELEM_IMAGE:
            return
        elif name == _ELEM_TILE_OFFSET:
            tile_offset = self.stack.pop()
            self.stack[-1][_ELEM_TILE_OFFSET] = tile_offset
            return

        self.logger.warn("endElement '%s' was unhandled", name)

    def startDocument(self):
        self.logger.debug("start document " + self.file_name)

    def endDocument(self):
        self.logger.debug("end document " + self.file_name)

    def characters(self, content):
        self.logger.debug("content: %s", content)
        return
        # self.logger.warn("content was unhandled: %s", content)

    def parse(self, file_name):
        self.file_name = file_name
        xml.sax.parse(file_name, self)
        return self.map_as_json


def convert_tmx_to_json(tmx_file_to_parse, logger=None):
    """
    Converts a tmx file in xml format into a json string.
    :param tmx_file_to_parse: the tmx file to parse.
    :param logger: the logger instance to use.
    :return: json string.
    """
    logging.basicConfig(level=logging.INFO)  # make sure that the root logger has DEBUG level set
    logger = logger or logging.getLogger(__name__)
    handler = Handler(logger)

    return handler.parse(tmx_file_to_parse)

#
# if __name__ == "__main__":
# import sys
#
#     if len(sys.argv) != 2:
#         print("missing map argument")
#
#     # parser = xml.sax.make_parser()
#     # parser.setContentHandler(Handler())
#     # parser.parse()
#     handler = Handler()
#     xml.sax.parse(sys.argv[1], handler)
#     print('!?', handler.map)
#
#     # name = sys.argv[1].replace("tmx", "json")
#     # import json
#     # d = json.load(open(name))
#     # json.dump(d, sys.stdout, sort_keys=True, indent=4)
