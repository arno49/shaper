#!/usr/bin/env python
# -*- coding: utf-8 -*-

from shaper import lib

from ._version import get_versions
__version__ = get_versions()['version']


__all__ = ["lib", "__version__"]
