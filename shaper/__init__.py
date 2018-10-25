#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Shaper (CMDB tool)
    Parse properties&configs to datastructure
    and create properties&configs from datastructure.

    Support ivan.bogomazov@gmail.com
    Minsk 2018
"""

from shaper import lib

from ._version import get_versions
__version__ = get_versions()['version']


__all__ = ["lib", "__version__"]
