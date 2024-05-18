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

from .pytmxloader import *


__version__ = '4.0.0.1'

# for easy comparison as in sys.version_info but digits only
__version_info__ = tuple([int(d) for d in __version__.split('.')])

__author__ = 'DR0ID'
__email__ = 'dr0iddr0id [at] googlemail [dot] com'
__copyright__ = "DR0ID @ 2014"
__credits__ = ["DR0ID"]  # list of contributors
__maintainer__ = "DR0ID"
__license__ = "New BSD license"

# __all__ = ['pytmxloader']
