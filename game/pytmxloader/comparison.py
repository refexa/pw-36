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
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the <organization> nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
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
from __future__ import print_function

__version__ = '1.0.0.0'

# for easy comparison as in sys.version_info but digits only
__version_info__ = tuple([int(d) for d in __version__.split('.')])

__author__ = "DR0ID"
__email__ = "dr0iddr0id {at} gmail [dot] com"
__copyright__ = "DR0ID @ 2016"
__credits__ = ["DR0ID"]  # list of contributors
__maintainer__ = "DR0ID"
__license__ = "New BSD license"

__all__ = ["EquatableMixin", "ComparableMixin", "NotComparableException"]  # list of public visible parts of this module


class NotComparableException(Exception):
    pass


class EquatableMixin(object):
    """
    This mixin allow to define when two instances of an object are 'equal'.

    According to the python help if __eq__ is implemented also the __hash__ method should implemented for
    immutable objects. For mutable objects the __hash__ method should be set to None (so they can't be used
    for hashable keys because it would lead to wrong results).

    Remember: only provide a __hash__ method for immutable types!

    Objects that can be tested for equality do not need to define an ordering. This is way an object inheriting
    from this mixin will not be comparable (for order) with other objects. It will raise a
    :class:`.NotComparableException`.

    For order comparisons the :class:`.ComparableMixin` exists.

    Base on: https://regebro.wordpress.com/2010/12/13/python-implementing-rich-comparison-the-correct-way/
    Adapted from: https://bugs.python.org/file21708/sane_total_ordering.py
    """

    def __eq__(self, other):
        """
        The 'equal' operator. Override this to define if two objects are equal, e.g.

            def __eq__(self, other):
                if isinstance(other, self):
                    return self.value == other.value
                return NotImplemented

        To compare for multiple values us either 'and' statements or a tuple.

        If this method does not know how to compare with the other type then it should 'return NotImplemented' to
        signal the runtime that this method does not know how to compare to the other object (the other object might
        know how to compare to this).

        :param other: the other instance to compare to.
        :return: True if the two objects are equal, False otherwise.
        """
        raise NotImplementedError()

    def __ne__(self, other):
        eq = self.__eq__(other)
        if eq is NotImplemented:
            return NotImplemented
        return not eq

    def __lt__(self, other):
        raise NotComparableException()

    def __le__(self, other):
        return NotComparableException()

    def __ge__(self, other):
        return NotComparableException()

    def __gt__(self, other):
        return NotComparableException()

    __hash__ = None


# noinspection PyAbstractClass
class ComparableMixin(EquatableMixin):
    """
    A class that implements all compare operations correctly reducing comparing two objects to implementing a two
    comparison method __lt__ and __eq__.

    Based on: https://regebro.wordpress.com/2010/12/13/python-implementing-rich-comparison-the-correct-way/
    Adapted from: https://bugs.python.org/file21708/sane_total_ordering.py

    """

    def __lt__(self, other):
        """
        The 'lower than' comparison method. Override this, e.g.

            def __lt__(self, other):
                if isinstance(other, self):
                    return self.value < other.value
                return NotImplemented

        The 'return NotImplemented' signals the runtime that this comparison method does not know how to compare
        to the other type.

        :param other: the other object to compare to.
        :return: True if this instance is < than the other, False otherwise.
        """
        raise NotImplementedError()

    def __ge__(self, other):
        lt = self.__lt__(other)
        if lt is NotImplemented:
            return NotImplemented
        return not lt

    def __le__(self, other):
        lt = self.__lt__(other)
        eq = self.__eq__(other)
        if lt is NotImplemented or eq is NotImplemented:
            return NotImplemented
        return lt or eq

    def __gt__(self, other):
        le = self.__le__(other)
        if le is NotImplemented:
            return NotImplemented
        return not le
