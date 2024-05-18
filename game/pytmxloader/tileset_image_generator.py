#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# New BSD license
#
# Copyright (c) DR0ID
# This file is part of HG_pytmxloader
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



__version__ = '1.0.0.0'

# for easy comparison as in sys.version_info but digits only
__version_info__ = tuple([int(d) for d in __version__.split('.')])

__author__ = "DR0ID"
__email__ = "dr0iddr0id {at} gmail [dot] com"
__copyright__ = "DR0ID @ 2014"
__credits__ = ["DR0ID"]  # list of contributors
__maintainer__ = "DR0ID"
__license__ = "New BSD license"

__all__ = []  # list of public visible parts of this module 

import argparse
import logging
import os


def get_tile_coordinates(num_tiles_x, num_tiles_y, tile_width, tile_height, margin, spacing, logger=None):
    """
    Returns a list of topleft coordinates of the tiles in the image. It is assumed the the coordinate system has its
        origin at topleft (positive y axis going down).
    :param num_tiles_x: number of tiles in x
    :param num_tiles_y: number of tiles in y
    :param tile_width: the tile width in pixels
    :param tile_height: the tile height in pixels
    :param margin: the margin around the tiles in pixels
    :param spacing: the spacing between tiles in pixels
    :param logger: the logging instance
    :return: [(x1, y1), (x2, y2), ....]
    """
    logger = logger or logging.getLogger(__name__)
    logger.debug(
        "Generating coordinates with args: num tiles x: %s num tiles y: %s "
        "tile w: %s tile h: %s margin: %s spacing: %s",
        num_tiles_x, num_tiles_y, tile_width, tile_height, margin, spacing)
    coordinates = []
    for y in range(margin, (tile_height + spacing) * num_tiles_y + margin, tile_height + spacing):
        for x in range(margin, (tile_width + spacing) * num_tiles_x + margin, tile_width + spacing):
            coordinates.append((x, y))
    logger.debug("Generated coordinates: %s", coordinates)
    return coordinates


def main(args=None, logger=None):
    """
    The main function of the program (the entry point).
    :param args:
        The command line arguments. When None the sys.argv arguments are used, otherwise the passed list of strings.
    :param logger:
        The logging instance.
    """
    parser = argparse.ArgumentParser(
        description="Create a image with a checkerboard pattern. It uses pygame (>= 1.8) to create the file.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('filename',
                        help="A filename to store the generated image (e.g. 'checkers.png'),"
                             " supports following formats: BMP, TGA, PNG, JPEG. "
                             "If the filename extension is unrecognized it will default to TGA. "
                             "Both TGA, and BMP file formats create uncompressed files.")

    # grid_group = parser.add_argument_group("grid", "grid options")
    parser.add_argument('num_tiles_x', type=int, help="Number of tiles in x direction, greater than 0.")
    parser.add_argument('num_tiles_y', type=int, help="Number of tiles in y direction, greater than 0.")
    parser.add_argument('--tile_width', type=int, default=32, help="The width of the tiles in pixels, greater than 0.")
    parser.add_argument('--tile_height', type=int, default=32,
                        help="The height of the tiles in pixels, greater than 0.")
    parser.add_argument('-s', '--spacing', type=int, default=0,
                        help="The spacing in pixels between the tiles, greater or equal to 0")

    parser.add_argument('-m', '--margin', type=int, default=0,
                        help="The margin around the tiles in pixels in this image, greater or equal to 0.")
    parser.add_argument('--image_width', type=int, default=None,
                        help="the with of the image, has to be bigger than"
                             " (tile_width + spacing) * num_tiles_x - spacing + 2 * margin"
                             ", otherwise warning is logged. Should be greater than 0.")
    parser.add_argument('--image_height', type=int, default=None,
                        help="the height of the image, has to be bigger than "
                             "(tile_height + spacing) * num_tiles_y - spacing + 2 * margin"
                             ", otherwise a warning is logged. Should be greater than 0.")
    parser.add_argument('--back_ground_color', default="FF00FFFF",
                        help="The color used for the margin and the spacing between the tiles, format is 'rrggbbaa'")
    parser.add_argument('--color1', default="000000FF",
                        help="The first color for the alternate colors of the tiles, format is 'rrggbbaa'")
    parser.add_argument('--color2', default="FFFFFFFF",
                        help="The second color for the alternate colors of the tiles, format is 'rrggbbaa'")
    parser.add_argument('-f', '--force', action='store_true', help="Try to override existing file.")

    excl_group = parser.add_mutually_exclusive_group()
    excl_group.add_argument('-v', '--verbose', action='store_const', const=logging.DEBUG,
                            dest='log_level', help='Verbose (debug) logging.')
    excl_group.add_argument('-q', '--quiet', action='store_const',
                            const=logging.WARN, dest='log_level', help='Silent mode, only log warnings.')

    parser.add_argument('--dry-run', action='store_true', help='Do nothing, do not write anything.')

    args = parser.parse_args(args=args)

    if logger is None:
        logger = logging.getLogger(__name__)
        logger.level = args.log_level or logging.INFO

    logger.debug(args)

    min_image_height = (args.tile_height + args.spacing) * args.num_tiles_y - args.spacing + 2 * args.margin
    logger.debug("Image min height: %s", min_image_height)
    if args.image_height is None:
        args.image_height = min_image_height

    min_image_width = (args.tile_width + args.spacing) * args.num_tiles_x - args.spacing + 2 * args.margin
    logger.debug("Image min width: %s", min_image_width)
    if args.image_width is None:
        args.image_width = min_image_width

    if args.image_height < min_image_height:
        logger.warn("Image height '%s' is smaller than the height of all tiles '%s', image will be cropped",
                    args.image_height, min_image_height)

    if args.image_width < min_image_width:
        logger.warn("Image width '%s' is smaller than the width of all tiles '%s', image will be cropped",
                    args.image_width, min_image_width)

    logger.debug("Image size: (%s, %s)", args.image_width, args.image_height)

    coordinates = get_tile_coordinates(args.num_tiles_x, args.num_tiles_y, args.tile_width, args.tile_height,
                                       args.margin,
                                       args.spacing)

    import pygame

    surf = pygame.Surface((args.image_width, args.image_height),
                          flags=pygame.SRCALPHA)  # , flags=0, depth=0, masks=None)
    surf.fill(pygame.Color("#" + args.back_ground_color))
    rect = pygame.Rect(0, 0, args.tile_width, args.tile_height)
    color1 = pygame.Color("#" + args.color1)
    color2 = pygame.Color("#" + args.color2)
    for index, coordinate in enumerate(coordinates):
        rect.topleft = coordinate
        column = index % args.num_tiles_x
        row = index // args.num_tiles_x
        color = color1 if (column + row) % 2 == 0 else color2
        surf.fill(color, rect)

    try:
        if args.dry_run:
            logger.info("***DRY-RUN*** would overwrite '%s'", args.filename)
            return
        else:
            if os.path.exists(args.filename) and not args.force:
                logging.error("File '%s' already exists, use -force ot overwrite it", args.filename)
                return
            else:
                logger.debug("Trying to write '%s'", args.filename)
                if args.force:
                    logger.info("Overwriting file '%s'", args.filename)
                pygame.image.save(surf, args.filename)
                logger.debug("File '%s' written", args.filename)
    except Exception:
        logger.error("Failed to write file '%s'", args.filename, exc_info=True)
    finally:
        logger.info("Done.")


def generate_test_images(path=""):
    """
    Generates various test images, with different settings.

    :param path:
        A path prefix, should contain trailing slash, e.g. '../tests/resources/' (best constructed using os.path.join)
    """
    main([os.path.join(path, 'tiles01_tiles8x5_size32x32_m0_s0.png'), '8', '5', '-m 0', '-s 0', '-v'])
    main([os.path.join(path, 'tiles02_tiles8x5_size32x32_m10_s0.png'), '8', '5', '-m 10', '-s 0', '-v'])
    main([os.path.join(path, 'tiles03_tiles8x5_size32x32_m0_s10.png'), '8', '5', '-m 0', '-s 10', '-v'])
    main([os.path.join(path, 'tiles04_tiles8x5_size32x32_m0_s9.png'), '8', '5', '-m 0', '-s 9', '-v'])
    main([os.path.join(path, 'tiles05_tiles8x5_size32x32_m11_s9.png'), '8', '5', '-m 11', '-s 9', '-v'])
    main([os.path.join(path, 'tiles06_tiles8x5_size32x32_m11_s8.png'), '8', '5', '-m 11', '-s 8', '-v'])
    main([os.path.join(path, 'tiles07_tiles8x2_size32x64_m0_s0.png'), '8', '5', '-m 0', '-s 0', '--tile_height=64',
          '-v'])
    main(
        [os.path.join(path, 'tiles08_tiles8x2_size64x32_m0_s0.png'), '8', '5', '-m 0', '-s 0', '--tile_width=64', '-v'])
    main([os.path.join(path, 'tiles09_tiles8x2_size32x64_m5_s5.png'), '8', '5', '-m 5', '-s 5', '--tile_height=64',
          '-v'])
    main(
        [os.path.join(path, 'tiles10_tiles8x2_size64x32_m5_s5.png'), '8', '5', '-m 5', '-s 5', '--tile_width=64', '-v'])
    main([os.path.join(path, 'tiles11_tiles8x2_size32x64_m0_s5.png'), '8', '5', '-m 0', '-s 5', '--tile_height=64',
          '-v'])
    main(
        [os.path.join(path, 'tiles12_tiles8x2_size64x32_m0_s5.png'), '8', '5', '-m 0', '-s 5', '--tile_width=64', '-v'])
    main([os.path.join(path, 'tiles13_tiles8x2_size32x64_m5_s0.png'), '8', '5', '-m 5', '-s 0', '--tile_height=64',
          '-v'])
    main(
        [os.path.join(path, 'tiles14_tiles8x2_size64x32_m5_s0.png'), '8', '5', '-m 5', '-s 0', '--tile_width=64', '-v'])
    main([os.path.join(path, 'tiles15_tiles8x2_size32x32_m5_s5.png'), '8', '5', '-m 5', '-s 5', '-v',
          '--back_ground_color=FF00FF00'])


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)  # make sure that the root logger has DEBUG level set
    main()

    # generate_test_images(os.path.join(os.pardir, 'tests', 'resources'))


