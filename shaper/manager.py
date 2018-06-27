#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

import fnmatch
import os

from collections import OrderedDict

from shaper import lib
from shaper.lib.configi import FILE_TYPES


def walk_on_path(path):
    """recursive find files with pattern"""
    matches = []
    for pattern, _ in FILE_TYPES.items():
        for root, _dirnames, files in os.walk(path):
            for filename in fnmatch.filter(files, '*{}'.format(pattern)):
                matches.append(os.path.join(root, filename))

    return matches


def read_properties(path_to_dir):
    """interface for recursive read properties"""
    data = {}
    files = walk_on_path(path_to_dir)

    for filename in files:
        data.update({
            filename: lib.read(filename)
        })

    return data


def create_folders(path_to_folder):
    """recursive creating folders"""
    try:
        os.makedirs(path_to_folder)
    except OSError:
        if os.path.isdir(path_to_folder):
            pass
        else:
            raise EOFError


def write_properties(datastructure, out_path):
    """interface for recursive write properties"""
    for filename, properties in datastructure.items():
        directories = os.path.join(
            out_path,
            os.path.dirname(filename)
        )
        property_file = os.path.basename(filename)
        create_folders(directories)
        lib.write(
            os.path.join(
                directories,
                property_file
            ),
            properties
        )


def forward_path_parser(_input):
    """parsing plain dict to nested"""

    def get_or_create_by_key(key, current_tree):
        """update dict by key"""
        if key not in current_tree:
            last = keys.pop()
            dict_update = {last: value}

            for _key in reversed(keys):
                dict_update = {_key: dict_update}

            current_tree.update(dict_update)
        else:
            keys.pop(0)
            get_or_create_by_key(keys[0], current_tree[key])

    output = {}
    for key, value in OrderedDict(_input).items():
        keys = key.split('/')

        get_or_create_by_key(keys[0], output)

    return output


def backward_path_parser(_input):
    """make nested structure plain"""

    def path_builder(current_tree, key=''):
        """make plain"""
        for _key, _value in current_tree.items():
            _key = key + '/' + _key if key else _key
            if '.' in _key:
                output.update({_key: _value})
            else:
                path_builder(_value, _key)

    output = {}
    path_builder(_input)

    return output
