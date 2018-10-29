#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Shaper (CMDB tool)
    Lib for manipulating files: read/write

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

import os
import sys
import json

from collections import OrderedDict
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
from xml.dom.minidom import parseString

import dicttoxml
import xmltodict

import oyaml as yaml


try:
    import ConfigParser
except ImportError:
    import configparser as ConfigParser


def read_plain_text(path_to_file):
    """
    Read plaintext file

    :param path_to_file: path to file
    :return: str

    :return: list of lines of string
    :rtype: [list, str]
    """
    try:
        with open(path_to_file, 'r') as _fd:
            return _fd.read()

    except (ValueError, OSError, IOError) as error:
        sys.stderr.write("Failed to read file {0}: {1}".format(
            path_to_file,
            error
        ))


def write_plain_text(path_to_file, content):
    """
    Write plaintext file

    :param path_to_file: path to file
    :return: str

    :param content: file content
    :return: str

    :return: None
    :rtype: None
    """
    try:
        with open(path_to_file, 'wb') as _fd:
            _fd.write(content)

    except (ValueError, OSError, IOError) as error:
        sys.stderr.write(
            "Failed to write file {0}: {1}".format(path_to_file, error),
        )


def read_yaml(path_to_file):
    """YAML read
    :param path_to_file: path to yaml file
    :type path_to_file: str

    :return: datastructure
    :rtype: dict
    """
    return yaml.load(read_plain_text(path_to_file))


def write_yaml(path_to_file, data):
    """Dump datastructure to yaml

    :param path_to_file: filepath
    :type path_to_file: str

    :param data: configuration dataset
    :type data: dict

    :return: None
    :rtype: None

    """
    content = yaml.dump(
        data,
        default_flow_style=False,
        allow_unicode=True,
    )

    write_plain_text(path_to_file, content)


def read_json(path_to_file):
    """JSON read
    :param path_to_file: path to yaml file
    :type path_to_file: str

    :return: json datastructure
    :rtype: dict
    """
    return json.load(path_to_file)


def write_json(path_to_file, data):
    """Dump datastructure to json

    :param path_to_file: filepath
    :type path_to_file: str

    :param data: configuration dataset
    :type data: dict

    :return: None
    :rtype: None

    """
    json.dump(
        data,
        path_to_file,
        indent=4,
        separators=(',', ': '),
        encoding="utf-8"
    )


def read_xml(path_to_file):
    """XML read
    :param path_to_file: path to yaml file
    :type path_to_file: str

    :return: XML datastructure
    :rtype: dict
    """

    return xmltodict.parse(read_plain_text(path_to_file))


def write_xml(path_to_file, data):
    """Dump datastructure to xml

    :param path_to_file: filepath
    :type path_to_file: str

    :param data: configuration dataset
    :type data: dict

    :return: None
    :rtype: None

    """
    dom = parseString(
        dicttoxml.dicttoxml(
            data,
            attr_type=False,
            root=False
        )
    )

    write_plain_text(
        path_to_file,
        dom.toprettyxml(encoding="utf-8")
    )


def read_property(path_to_file):
    """PROPERTY read
    :param path_to_file: path to property file
    :type path_to_file: str

    :return: property datastructure
    :rtype: dict
    """
    content = read_plain_text(path_to_file)

    config = StringIO()
    config.write('[dummy_section]\n')
    config.write(content.replace('%', '%%'))
    config.seek(0, os.SEEK_SET)

    conf_parser = ConfigParser.SafeConfigParser()
    # pylint: disable=deprecated-method
    conf_parser.readfp(config)

    return OrderedDict(conf_parser.items('dummy_section'))


def write_property(path_to_file, data):
    """Dump datastructure to property

    :param path_to_file: filepath
    :type path_to_file: str

    :param data: configuration dataset
    :type data: dict

    :return: None
    :rtype: None

    """
    write_plain_text(
        path_to_file,
        "\n".join([
            "{}={}".format(
                item[0],
                item[1]
            ) for item in data.items()
        ])
    )


FILE_TYPES = {
    ".json": (read_json, write_json),
    ".yml": (read_yaml, write_yaml),
    ".yaml": (read_yaml, write_yaml),
    ".xml": (read_xml, write_xml),
    ".properties": (read_property, write_property),
    ".txt": (read_plain_text, write_plain_text),
    "": (read_plain_text, write_plain_text),
}


def type_choise(path_to_file):
    """
    Set type of file.

    :param path_to_file: path to file
    :type path_to_file: str

    :return: File typo parser
    :rtype: parser
    """

    extension = os.path.splitext(path_to_file)[-1]
    if extension not in FILE_TYPES:
        print(
            "Unknown file extension in {}".format(
                path_to_file
            )
        )
        return None, None
    return FILE_TYPES.get(extension)


def read(path_to_file, file_type="auto"):
    """
    Read file datastructure according its type.

    Default type choose dynamic with magic function.

    :param path_to_file: path to file
    :type path_to_file: str

    :return: File datastructure
    :rtype: [dict, list]

    """

    if file_type == "auto":
        parser = type_choise(path_to_file)[0]
    else:
        parser = FILE_TYPES.get(file_type)

    if parser:
        try:
            return parser(path_to_file)

        # pylint: disable=broad-except
        # disable cause of list of exceptions
        # not known due to a lot of parsers
        except Exception as except_details:
            except_message = "Failed to parse {}".format(
                os.path.abspath(path_to_file)
            )

            print("{}\n{}".format(
                except_message,
                except_details
            ))
            return except_message

    else:
        return {
            "msg": "Unsupported file extension"
        }


def write(path_to_file, data, file_type="auto"):
    """
    Write datastructure in file according its type.

    Default type choose dynamic with magic function.

    :param path_to_file: path to file
    :type path_to_file: str

    :param data: datastructure
    :type data: [str, dict, list]

    :return: None
    :rtype: None

    """

    if file_type == "auto":
        parser = type_choise(path_to_file)[1]
    else:
        parser = FILE_TYPES.get(file_type)

    return parser(path_to_file, data)
