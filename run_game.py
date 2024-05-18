# -*- coding: utf-8 -*-

from __future__ import print_function

import logging

from game import main

level = logging.DEBUG if __debug__ else logging.WARNING
logging.basicConfig(level=level, force=True)
main.main()
