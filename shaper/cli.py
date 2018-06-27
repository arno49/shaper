#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Shaper (CMDB tool)
    Parse properties&configs to datastructure
    and create properties&configs from datastructure.

    Support ivan.bogomazov@gmail.com
    Minsk 2018


    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    EXAMPLES:
        TBD
"""

from __future__ import print_function, unicode_literals

import argparse
import fnmatch
import os

from collections import OrderedDict

from shaper import lib
from shaper import manager
from shaper.lib.configi import FILE_TYPES


def parse_arguments():
    """Argument parsing

    :return: args namespace
    :rtype: namespace
    """
    parser = argparse.ArgumentParser(
        description='Tool to manage java properties'
    )

    parser.add_argument(
        "-v",
        dest="logging",
        action="count",
        default=0,
        help="Verbose output"
    )

    subparsers = parser.add_subparsers(
        dest="parser"
    )

    read = subparsers.add_parser(
        "read",
        help="Recursive read properties from files"
    )

    write = subparsers.add_parser(
        "write",
        help="Write properties files from datastructure"
    )

    play = subparsers.add_parser(
        "play",
        help="Run playbook like ansible"
    )

    read.add_argument(
        'src_path',
        type=str,
        help='Path to properties directory',
    )

    read.add_argument(
        '-o',
        '--out',
        dest='out',
        default='out.yml',
        help='Output file. Default out.yaml',
    )

    write.add_argument(
        "src_structure",
        type=str,
        help="Path to yaml with datastructure."
    )

    write.add_argument(
        '-o',
        '--out',
        dest='out',
        default='./out/',
        help='Path to output directory. Default ./out/',
    )

    write.add_argument(
        '-k',
        '--key',
        dest='key',
        default=None,
        help='Key for rendering custom subtree. Default render from root',
    )

    play.add_argument(
        'src_path',
        type=str,
        help='Path to playbook',
    )

    return parser.parse_args()


def main():
    """main"""
    arguments = parse_arguments()

    if arguments.parser == "read":
        tree = manager.forward_path_parser(
            manager.read_properties(
                arguments.src_path
            )
        )

        lib.write(arguments.out, tree)

    elif arguments.parser == "write":
        yaml_data = lib.read(arguments.src_structure)
        datastructure = manager.backward_path_parser(yaml_data)

        # filter render files by key
        if arguments.key:
            datastructure = OrderedDict(
                (key, value)
                for key, value in datastructure.items()
                if arguments.key in key
            )

        if arguments.logging:
            print("==> Files to render :")
            print('\n'.join(datastructure.keys()))

        manager.write_properties(datastructure, arguments.out)

    else:
        raise NotImplementedError


if __name__ == "__main__":
    main()
