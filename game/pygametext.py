# -*- coding: utf-8 -*-
"""
# ptext module: place this in your import directory.

# ptext.draw(text, pos=None, **options)

# Please see README.md for explanation of options.
# https://github.com/cosmologicon/pygame-text
"""

from __future__ import division

from math import ceil, sin, cos, radians, exp

import pygame

__version__ = '1.0.0'
__author__ = 'Cosmologicon, (c) 2015-2017'
__vernum__ = tuple(int(s) for s in __version__.split('.'))
__all__ = [
    'DEFAULT_FONT_SIZE', 'REFERENCE_FONT_SIZE', 'DEFAULT_LINE_HEIGHT', 'DEFAULT_PARAGRAPH_SPACE',
    'DEFAULT_FONT_NAME', 'FONT_NAME_TEMPLATE',
    'DEFAULT_COLOR', 'DEFAULT_BACKGROUND',
    'DEFAULT_SHADE', 'DEFAULT_SHADOW_COLOR', 'SHADOW_UNIT',
    'DEFAULT_OUTLINE_COLOR', 'OUTLINE_UNIT',
    'DEFAULT_ALIGN', 'DEFAULT_ANCHOR', 'DEFAULT_STRIP',
    'ALPHA_RESOLUTION', 'ANGLE_RESOLUTION_DEGREES',
    'AUTO_CLEAN', 'MEMORY_LIMIT_MB', 'MEMORY_REDUCTION_FACTOR',

    'getfont', 'wrap', 'getsurf', 'draw', 'drawbox', 'clean',
]
# todo update to newest version?

DEFAULT_FONT_SIZE = 24
REFERENCE_FONT_SIZE = 100
DEFAULT_LINE_HEIGHT = 1.0
DEFAULT_PARAGRAPH_SPACE = 0.0
DEFAULT_FONT_NAME = None
FONT_NAME_TEMPLATE = "%s"
DEFAULT_COLOR = "white"
DEFAULT_BACKGROUND = None
DEFAULT_SHADE = 0
DEFAULT_OUTLINE_COLOR = "black"
DEFAULT_SHADOW_COLOR = "black"
OUTLINE_UNIT = 1 / 24
SHADOW_UNIT = 1 / 18
DEFAULT_ALIGN = "left"  # left, center, or right
DEFAULT_ANCHOR = 0, 0  # 0, 0 = top left ;  1, 1 = bottom right
DEFAULT_STRIP = True
ALPHA_RESOLUTION = 16
ANGLE_RESOLUTION_DEGREES = 3

AUTO_CLEAN = True
MEMORY_LIMIT_MB = 64
MEMORY_REDUCTION_FACTOR = 0.5

pygame.font.init()

_font_cache = {}


def getfont(fontname=None, fontsize=None, sysfontname=None,
            bold=None, italic=None, underline=None):
    if fontname is not None and sysfontname is not None:
        raise ValueError("Can't set both fontname and sysfontname")
    if fontname is None and sysfontname is None:
        fontname = DEFAULT_FONT_NAME
    if fontsize is None:
        fontsize = DEFAULT_FONT_SIZE
    key = fontname, fontsize, sysfontname, bold, italic, underline
    if key in _font_cache:
        return _font_cache[key]
    if sysfontname is not None:
        font = pygame.font.SysFont(sysfontname, fontsize, bold or False, italic or False)
    else:
        if fontname is not None:
            fontname = FONT_NAME_TEMPLATE % fontname
        try:
            font = pygame.font.Font(fontname, fontsize)
        except IOError:
            raise IOError("unable to read font filename: %s" % fontname)
    if bold is not None:
        font.set_bold(bold)
    if italic is not None:
        font.set_italic(italic)
    if underline is not None:
        font.set_underline(underline)
    _font_cache[key] = font
    return font


def wrap(text, fontname=None, fontsize=None, sysfontname=None,
         bold=None, italic=None, underline=None, width=None, widthem=None, strip=None):
    if widthem is None:
        font = getfont(fontname, fontsize, sysfontname, bold, italic, underline)
    elif width is not None:
        raise ValueError("Can't set both width and widthem")
    else:
        font = getfont(fontname, REFERENCE_FONT_SIZE, sysfontname, bold, italic, underline)
        width = widthem * REFERENCE_FONT_SIZE
    if strip is None:
        strip = DEFAULT_STRIP
    paras = text.replace("\t", "    ").split("\n")
    lines = []
    for jpara, para in enumerate(paras):
        if strip:
            para = para.rstrip(" ")
        if width is None:
            lines.append((para, jpara))
            continue
        if not para:
            lines.append(("", jpara))
            continue
        # Preserve leading spaces in all cases.
        a = len(para) - len(para.lstrip(" "))
        # At any time, a is the rightmost known index you can legally split a line. I.e. it's legal
        # to add para[:a] to lines, and line is what will be added to lines if para is split at a.
        a = para.index(" ", a) if " " in para else len(para)
        line = para[:a]
        while a + 1 < len(para):
            # b is the next legal place to break the line, with bline the corresponding line to add.
            if " " not in para[a + 1:]:
                b = len(para)
                bline = para
            elif strip:
                # Lines may be split at any space character that immediately follows a non-space
                # character.
                b = para.index(" ", a + 1)
                while para[b - 1] == " ":
                    if " " in para[b + 1:]:
                        b = para.index(" ", b + 1)
                    else:
                        b = len(para)
                        break
                bline = para[:b]
            else:
                # Lines may be split at any space character, or any character immediately following
                # a space character.
                b = a + 1 if para[a] == " " else para.index(" ", a + 1)
            bline = para[:b]
            if font.size(bline)[0] <= width:
                a, line = b, bline
            else:
                lines.append((line, jpara))
                para = para[a:].lstrip(" ") if strip else para[a:]
                a = para.index(" ", 1) if " " in para[1:] else len(para)
                line = para[:a]
        if para:
            lines.append((line, jpara))
    return lines


_fit_cache = {}


def _fitsize(text, fontname, sysfontname, bold, italic, underline, width, height, lineheight, pspace, strip):
    key = text, fontname, sysfontname, bold, italic, underline, width, height, lineheight, pspace, strip
    if key in _fit_cache:
        return _fit_cache[key]

    def fits(fontsize):
        texts = wrap(text, fontname, fontsize, sysfontname, bold, italic, underline, width, strip)
        font = getfont(fontname, fontsize, sysfontname, bold, italic, underline)
        w = max(font.size(line)[0] for line, jpara in texts)
        linesize = font.get_linesize() * lineheight
        paraspace = font.get_linesize() * pspace
        h = int(round((len(texts) - 1) * linesize + texts[-1][1] * paraspace)) + font.get_height()
        return w <= width and h <= height

    a, b = 1, 256
    if not fits(a):
        fontsize = a
    elif fits(b):
        fontsize = b
    else:
        while b - a > 1:
            c = (a + b) // 2
            if fits(c):
                a = c
            else:
                b = c
        fontsize = a
    _fit_cache[key] = fontsize
    return fontsize


def _resolvecolor(color, default):
    if color is None:
        color = default
    if color is None:
        return None
    try:
        return tuple(pygame.Color(color))
    except ValueError:
        return tuple(color)


def _applyshade(color, shade):
    f = exp(-0.4 * shade)
    r, g, b = [
        min(max(int(round((c + 50) * f - 50)), 0), 255)
        for c in color[:3]
    ]
    return (r, g, b) + tuple(color[3:])


def _resolvealpha(alpha):
    if alpha >= 1:
        return 1
    return max(int(round(alpha * ALPHA_RESOLUTION)) / ALPHA_RESOLUTION, 0)


def _resolveangle(angle):
    if not angle:
        return 0
    angle %= 360
    return int(round(angle / ANGLE_RESOLUTION_DEGREES)) * ANGLE_RESOLUTION_DEGREES


# Return the set of points in the circle radius r, using Bresenham's circle algorithm
_circle_cache = {}


def _circlepoints(r):
    r = int(round(r))
    if r in _circle_cache:
        return _circle_cache[r]
    x, y, e = r, 0, 1 - r
    _circle_cache[r] = points = []
    while x >= y:
        points.append((x, y))
        y += 1
        if e < 0:
            e += 2 * y - 1
        else:
            x -= 1
            e += 2 * (y - x) - 1
    points += [(y, x) for x, y in points if x > y]
    points += [(-x, y) for x, y in points if x]
    points += [(x, -y) for x, y in points if y]
    points.sort()
    return points


_surf_cache = {}
_surf_tick_usage = {}
_surf_size_total = 0
_unrotated_size = {}
_tick = 0


def getsurf(text, fontname=None, fontsize=None, sysfontname=None, bold=None, italic=None,
            underline=None, width=None, widthem=None, strip=None, color=None,
            background=None, antialias=True, ocolor=None, owidth=None, scolor=None, shadow=None,
            gcolor=None, shade=None, alpha=1.0, align=None, lineheight=None, pspace=None, angle=0,
            cache=True):
    global _tick, _surf_size_total
    if fontname is None:
        fontname = DEFAULT_FONT_NAME
    if fontsize is None:
        fontsize = DEFAULT_FONT_SIZE
    fontsize = int(round(fontsize))
    if align is None:
        align = DEFAULT_ALIGN
    if align in ["left", "center", "right"]:
        align = [0, 0.5, 1][["left", "center", "right"].index(align)]
    if lineheight is None:
        lineheight = DEFAULT_LINE_HEIGHT
    if pspace is None:
        pspace = DEFAULT_PARAGRAPH_SPACE
    color = _resolvecolor(color, DEFAULT_COLOR)
    background = _resolvecolor(background, DEFAULT_BACKGROUND)
    gcolor = _resolvecolor(gcolor, None)
    if shade is None:
        shade = DEFAULT_SHADE
    if shade:
        gcolor = _applyshade(gcolor or color, shade)
        shade = 0
    ocolor = None if owidth is None else _resolvecolor(ocolor, DEFAULT_OUTLINE_COLOR)
    scolor = None if shadow is None else _resolvecolor(scolor, DEFAULT_SHADOW_COLOR)
    opx = None if owidth is None else ceil(owidth * fontsize * OUTLINE_UNIT)
    spx = None if shadow is None else tuple(ceil(s * fontsize * SHADOW_UNIT) for s in shadow)
    alpha = _resolvealpha(alpha)
    angle = _resolveangle(angle)
    strip = DEFAULT_STRIP if strip is None else strip
    key = (text, fontname, fontsize, sysfontname, bold, italic, underline, width, widthem, strip,
           color, background, antialias, ocolor, opx, scolor, spx, gcolor, alpha, align, lineheight,
           pspace, angle)
    if key in _surf_cache:
        _surf_tick_usage[key] = _tick
        _tick += 1
        return _surf_cache[key]
    texts = wrap(text, fontname, fontsize, sysfontname, bold, italic, underline,
                 width=width, widthem=widthem, strip=strip)
    if angle:
        surf0 = getsurf(text, fontname, fontsize, sysfontname, bold, italic, underline,
                        width, widthem, strip, color, background, antialias,
                        ocolor, owidth, scolor, shadow, gcolor, 0, alpha, align, lineheight, pspace,
                        cache=cache)
        if angle in (90, 180, 270):
            surf = pygame.transform.rotate(surf0, angle)
        else:
            surf = pygame.transform.rotozoom(surf0, angle, 1.0)
        _unrotated_size[(surf.get_size(), angle, text)] = surf0.get_size()
    elif alpha < 1.0:
        surf0 = getsurf(text, fontname, fontsize, sysfontname, bold, italic, underline,
                        width, widthem, strip, color, background, antialias,
                        ocolor, owidth, scolor, shadow, gcolor=gcolor, shade=0, align=align,
                        lineheight=lineheight, pspace=pspace, cache=cache)
        surf = surf0.copy()
        _surf = surf0.copy()
        _surf.fill((255, 255, 255, int(alpha * 255.0)))
        surf.blit(_surf, (0, 0), None, pygame.BLEND_RGBA_MULT)
        del _surf
        # array = pygame.surfarray.pixels_alpha(surf)
        # array[:, :] = (array[:, :] * alpha).astype(array.dtype)
        # del array

    elif spx is not None:
        surf0 = getsurf(text, fontname, fontsize, sysfontname, bold, italic, underline,
                        width, widthem, strip, color=color, background=(0, 0, 0, 0), antialias=antialias,
                        gcolor=gcolor, shade=0, align=align, lineheight=lineheight, pspace=pspace, cache=cache)
        ssurf = getsurf(text, fontname, fontsize, sysfontname, bold, italic, underline,
                        width, widthem, strip, color=scolor, background=(0, 0, 0, 0), antialias=antialias,
                        align=align, lineheight=lineheight, pspace=pspace, cache=cache)
        w0, h0 = surf0.get_size()
        sx, sy = spx
        surf = pygame.Surface((w0 + abs(sx), h0 + abs(sy))).convert_alpha()
        surf.fill(background or (0, 0, 0, 0))
        dx, dy = max(sx, 0), max(sy, 0)
        surf.blit(ssurf, (dx, dy))
        x0, y0 = abs(sx) - dx, abs(sy) - dy
        if len(color) > 3 and color[3] == 0:
            raise Exception("spx, color[3]==0")
            # array = pygame.surfarray.pixels_alpha(surf)
            # array0 = pygame.surfarray.pixels_alpha(surf0)
            # array[x0:x0 + w0, y0:y0 + h0] -= array0.clip(max=array[x0:x0 + w0, y0:y0 + h0])
            # del array, array0
            pass
        else:
            surf.blit(surf0, (x0, y0))
    elif opx is not None:
        surf0 = getsurf(text, fontname, fontsize, sysfontname, bold, italic, underline,
                        width, widthem, strip, color=color, background=(0, 0, 0, 0), antialias=antialias,
                        gcolor=gcolor, shade=0, align=align, lineheight=lineheight, pspace=pspace, cache=cache)
        osurf = getsurf(text, fontname, fontsize, sysfontname, bold, italic, underline,
                        width, widthem, strip, color=ocolor, background=(0, 0, 0, 0), antialias=antialias,
                        align=align, lineheight=lineheight, pspace=pspace, cache=cache)
        w0, h0 = surf0.get_size()
        surf = pygame.Surface((w0 + 2 * opx, h0 + 2 * opx)).convert_alpha()
        surf.fill(background or (0, 0, 0, 0))
        for dx, dy in _circlepoints(opx):
            surf.blit(osurf, (dx + opx, dy + opx))
        if len(color) > 3 and color[3] == 0:
            # array = pygame.surfarray.pixels_alpha(surf)
            # array0 = pygame.surfarray.pixels_alpha(surf0)
            # array[opx:-opx, opx:-opx] -= array0.clip(max=array[opx:-opx, opx:-opx])
            # del array, array0
            # raise Exception("opx, color[3] == 0")

            # _surf = surf0.copy()
            # _surf.fill((0, 0, 0, 0))
            # _surf.blit(surf, (0, 0), None, pygame.BLEND_RGBA_MAX)
            # surf0.blit(_surf, (0, 0), None, pygame.BLEND_RGBA_MULT)
            _surf = surf0.copy()
            _surf.fill((0, 0, 0, 255), None, pygame.BLEND_RGBA_MULT)
            surf.blit(_surf, (opx, opx), None, pygame.BLEND_RGBA_SUB)
            del _surf
        else:
            surf.blit(surf0, (opx, opx))
    else:
        font = getfont(fontname, fontsize, sysfontname, bold, italic, underline)
        # pygame.Font.render does not allow passing None as an argument value for background.
        if background is None or (len(background) > 3 and background[3] == 0) or gcolor is not None:
            lsurfs = [font.render(text, antialias, color).convert_alpha() for text, jpara in texts]
        else:
            lsurfs = [font.render(text, antialias, color, background).convert_alpha() for text, jpara in texts]
        if gcolor is not None:
            # import numpy
            # m = numpy.clip(numpy.arange(lsurfs[0].get_height()) * 2.0 / font.get_ascent() - 1.0, 0, 1)
            # for lsurf in lsurfs:
            #     array = pygame.surfarray.pixels3d(lsurf)
            #     for j in (0, 1, 2):
            #         array[:, :, j] = ((1.0 - m) * array[:, :, j] + m * gcolor[j]).astype(array.dtype)
            #     del array
            _surf_height = lsurfs[0].get_height()
            m = (_x * 2.0 / font.get_ascent() - 1.0 for _x in range(_surf_height))
            m = [0 if _x < 0 else (1 if _x > 1 else _x) for _x in m]
            for lsurf in lsurfs:
                grad1 = pygame.Surface((1, _surf_height))
                grad2 = pygame.Surface((1, _surf_height))
                for idx, _m_val in enumerate(m):
                    _inv_m_val = 1.0 - _m_val
                    _color = (int(round(_inv_m_val * 255)),
                              int(round(_inv_m_val * 255)),
                              int(round(_inv_m_val * 255)))
                    grad1.set_at((0, idx), _color)
                    _color = (int(round(_m_val * gcolor[0])),
                              int(round(_m_val * gcolor[1])),
                              int(round(_m_val * gcolor[2])))
                    grad2.set_at((0, idx), _color)
                grad1 = pygame.transform.scale(grad1, lsurf.get_size())
                grad2 = pygame.transform.scale(grad2, lsurf.get_size())
                lsurf.blit(grad1, (0, 0), None, pygame.BLEND_RGB_MULT)
                lsurf.blit(grad2, (0, 0), None, pygame.BLEND_RGB_ADD)
                del grad1
                del grad2

        if len(lsurfs) == 1 and gcolor is None:
            surf = lsurfs[0]
        else:
            w = max(lsurf.get_width() for lsurf in lsurfs)
            linesize = font.get_linesize() * lineheight
            parasize = font.get_linesize() * pspace
            ys = [int(round(k * linesize + jpara * parasize)) for k, (text, jpara) in enumerate(texts)]
            h = ys[-1] + font.get_height()
            surf = pygame.Surface((w, h)).convert_alpha()
            surf.fill(background or (0, 0, 0, 0))
            for y, lsurf in zip(ys, lsurfs):
                x = int(round(align * (w - lsurf.get_width())))
                surf.blit(lsurf, (x, y))
    if cache:
        w, h = surf.get_size()
        _surf_size_total += 4 * w * h
        _surf_cache[key] = surf
        _surf_tick_usage[key] = _tick
        _tick += 1
    return surf


_default_surf_sentinel = ()


def draw(text, pos=None,
         fontname=None, fontsize=None, sysfontname=None,
         antialias=True, bold=None, italic=None, underline=None,
         color=None, background=None,
         top=None, left=None, bottom=None, right=None,
         topleft=None, bottomleft=None, topright=None, bottomright=None,
         midtop=None, midleft=None, midbottom=None, midright=None,
         center=None, centerx=None, centery=None,
         width=None, widthem=None, lineheight=None, pspace=None, strip=None,
         align=None,
         owidth=None, ocolor=None,
         shadow=None, scolor=None,
         gcolor=None, shade=None,
         alpha=1.0,
         anchor=None,
         angle=0,
         surf=_default_surf_sentinel,
         cache=True):
    if topleft:
        left, top = topleft
    if bottomleft:
        left, bottom = bottomleft
    if topright:
        right, top = topright
    if bottomright:
        right, bottom = bottomright
    if midtop:
        centerx, top = midtop
    if midleft:
        left, centery = midleft
    if midbottom:
        centerx, bottom = midbottom
    if midright:
        right, centery = midright
    if center:
        centerx, centery = center

    x, y = pos or (None, None)
    hanchor, vanchor = anchor or (None, None)
    if left is not None:
        x, hanchor = left, 0
    if centerx is not None:
        x, hanchor = centerx, 0.5
    if right is not None:
        x, hanchor = right, 1
    if top is not None:
        y, vanchor = top, 0
    if centery is not None:
        y, vanchor = centery, 0.5
    if bottom is not None:
        y, vanchor = bottom, 1
    if x is None:
        raise ValueError("Unable to determine horizontal position")
    if y is None:
        raise ValueError("Unable to determine vertical position")

    if align is None:
        align = hanchor
    if hanchor is None:
        hanchor = DEFAULT_ANCHOR[0]
    if vanchor is None:
        vanchor = DEFAULT_ANCHOR[1]

    tsurf = getsurf(text, fontname, fontsize, sysfontname, bold, italic, underline, width, widthem,
                    strip, color, background, antialias, ocolor, owidth, scolor, shadow, gcolor, shade, alpha,
                    align, lineheight, pspace, angle, cache)
    angle = _resolveangle(angle)
    if angle:
        w0, h0 = _unrotated_size[(tsurf.get_size(), angle, text)]
        S, C = sin(radians(angle)), cos(radians(angle))
        dx, dy = (0.5 - hanchor) * w0, (0.5 - vanchor) * h0
        x += dx * C + dy * S - 0.5 * tsurf.get_width()
        y += -dx * S + dy * C - 0.5 * tsurf.get_height()
    else:
        x -= hanchor * tsurf.get_width()
        y -= vanchor * tsurf.get_height()
    x = int(round(x))
    y = int(round(y))

    if surf is _default_surf_sentinel:
        surf = pygame.display.get_surface()
    if surf is not None:
        surf.blit(tsurf, (x, y))

    if AUTO_CLEAN:
        clean()

    return tsurf, (x, y)


def drawbox(text, rect, fontname=None, sysfontname=None, lineheight=None, pspace=None, anchor=None,
            bold=None, italic=None, underline=None, strip=None, **kwargs):
    if fontname is None:
        fontname = DEFAULT_FONT_NAME
    if lineheight is None:
        lineheight = DEFAULT_LINE_HEIGHT
    if pspace is None:
        pspace = DEFAULT_PARAGRAPH_SPACE
    hanchor, vanchor = anchor = anchor or (0.5, 0.5)
    rect = pygame.Rect(rect)
    x = rect.x + hanchor * rect.width
    y = rect.y + vanchor * rect.height
    fontsize = _fitsize(text, fontname, sysfontname, bold, italic, underline,
                        rect.width, rect.height, lineheight, pspace, strip)
    return draw(text, (x, y), fontname=fontname, fontsize=fontsize, lineheight=lineheight,
                pspace=pspace, width=rect.width, strip=strip, anchor=anchor, **kwargs)


def clean():
    global _surf_size_total
    memory_limit = MEMORY_LIMIT_MB * (1 << 20)
    if _surf_size_total < memory_limit:
        return
    memory_limit *= MEMORY_REDUCTION_FACTOR
    keys = sorted(_surf_cache, key=_surf_tick_usage.get)
    for key in keys:
        w, h = _surf_cache[key].get_size()
        del _surf_cache[key]
        del _surf_tick_usage[key]
        _surf_size_total -= 4 * w * h
        if _surf_size_total < memory_limit:
            break
