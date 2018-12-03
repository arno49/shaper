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

import json
import os
import sys
from collections import OrderedDict
from xml.dom.minidom import parseString

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

import xmltodict
import yaml

from . import dicttoxml
from .loader import (
    OrderedDictYAMLLoader,
    represent_ordered_dict,
    represent_unicode,
    represent_multi_line,
)


class BaseParser(object):
    WARNING_MESSAGE = 'Warning. Unsupported file extension for {file}'

    @staticmethod
    def parsers_choice(filepath):
        """Get parser class by file type.

        :param filepath: string path to file
        :return: parser class
        """

        _, ext = os.path.splitext(filepath)

        return PARSERS_MAPPING.get(ext)

    def read(self, path):  # pylint: disable=inconsistent-return-statements
        """Read file data structure according its type. Default type choose
        dynamic with magic function.

        :param path: string path to file
        :return: File data structure
        :rtype: [dict, list]
        """

        parser_class = self.parsers_choice(path)
        if parser_class:
            try:
                return parser_class().read(path)

            # pylint: disable=broad-except
            # disable cause of list of exceptions
            # not known due to a lot of parsers
            except Exception as exc:
                msg = 'Failed to parse {file}'.format(file=os.path.abspath(path))
                sys.stderr.write(
                    '{message}\n{exception}'.format(message=msg, exception=exc),
                )

        sys.stderr.write(self.WARNING_MESSAGE.format(file=path))

    def write(self, data, path):
        """Write data in file according its type. Default type choose dynamic
        with magic function.

        :param path: string path to file
        :param data: data
        :type data: [str, dict, list]

        :return: None
        :rtype: None
        """

        parser_class = self.parsers_choice(path)
        if parser_class:
            parser_class().write(data, path)
        else:
            sys.stderr.write(self.WARNING_MESSAGE.format(file=path))


class TextParser(object):

    def read(self, path):
        """Read plaintext file.

        :param path: string path to file
        :return: list of lines of string
        :rtype: [list, str]
        """

        try:
            with open(path, 'r') as fd:
                return fd.read()

        except (ValueError, OSError, IOError) as exc:
            sys.stderr.write(
                'Failed to read {file}: {msg}'.format(file=path, msg=str(exc)),
            )

    def write(self, data, path):
        """Write plaintext file.

        :param data: file content
        :param path: string path to file
        :return: str

        :return: None
        :rtype: None
        """

        try:
            with open(path, 'wb') as fd:
                fd.write(data)

        except (ValueError, OSError, IOError) as exc:
            sys.stderr.write(
                'Failed to write {file}: {msg}'.format(file=path, msg=str(exc)),
            )


class YAMLParser(TextParser):

    def read(self, path):
        """YAML read.

        :param path: string path to file
        :return: data structure
        :rtype: dict
        """

        return yaml.load(
            super(YAMLParser, self).read(path),
            Loader=OrderedDictYAMLLoader,
        )

    def write(self, data, path):
        """Dump data structure to YAML.

        :param data: configuration dataset
        :param path: string path to file
        :type data: dict

        :return: None
        :rtype: None
        """

        yaml.add_representer(OrderedDict, represent_ordered_dict)
        if sys.version_info[0] == 2:
            yaml.add_representer(
                unicode,  # pylint: disable=undefined-variable
                represent_unicode,
            )

        # add string representer for multi line issue
        yaml.add_representer(str, represent_multi_line)

        content = yaml.dump(
            data,
            default_flow_style=False,
            allow_unicode=True,
        )

        if sys.version_info[0] == 3:
            content = bytearray(content, 'utf-8')

        super(YAMLParser, self).write(content, path)


class JSONParser(TextParser):

    def read(self, path):
        """JSON read.

        :param path: string path to file
        :return: json data structure
        :rtype: dict
        """

        return json.loads(super(JSONParser, self).read(path))

    def write(self, data, path):
        """Dump data to JSON.

        :param data: configuration data structure
        :param path: string path to file
        :type data: dict

        :return: None
        :rtype: None
        """

        kw = {'encoding': 'utf-8'} if sys.version_info[0] == 2 else {}
        with open(path, 'w') as fd:
            json.dump(
                data,
                fd,
                indent=4,
                separators=(',', ': '),
                **kw
            )


class XMLParser(TextParser):

    def read(self, path):
        """XML read.

        :param path: string path to file
        :return: XML data structure
        :rtype: dict
        """

        return xmltodict.parse(super(XMLParser, self).read(path))

    def write(self, data, path):
        """Dump data structure to XML.

        :param data: configuration data structure
        :param path: string path to file
        :type data: dict

        :return: None
        :rtype: None
        """

        dom = parseString(
            dicttoxml.dict_to_xml(
                data,
                fold_list=False,
                item_func=lambda x: x,
                attr_type=False,
                root=False,
            ),
        )

        super(XMLParser, self).write(dom.toprettyxml(encoding='utf-8'), path)


class PropertyParser(TextParser):

    @staticmethod
    def _process_multiline_string(string):
        string_splitted = string.splitlines()
        if len(string_splitted) > 1:
            return "\n  ".join(string_splitted)
        return string

    def read(self, path):
        """PROPERTY read.

        :param path: string path to file
        :return: property data structure
        :rtype: dict
        """

        try:
            import ConfigParser
        except ImportError:
            import configparser as ConfigParser

        content = super(PropertyParser, self).read(path)

        config = StringIO()
        config.write('[dummy_section]\n')
        config.write(content.replace('%', '%%'))
        config.seek(0, os.SEEK_SET)

        conf_parser = ConfigParser.SafeConfigParser()
        conf_parser.optionxform = str
        # pylint: disable=deprecated-method
        conf_parser.readfp(config)

        return OrderedDict(conf_parser.items('dummy_section'))

    def write(self, data, path):
        """Dump data structure to property.

        :param data: configuration data structure
        :param path: string path to file
        :type data: dict

        :return: None
        :rtype: None
        """

        stream = '\n'.join(
            '{}={}'.format(item[0], self._process_multiline_string(item[1])) for item in data.items(),
        )
        super(PropertyParser, self).write(
            stream.encode(encoding='utf-8'),
            path,
        )


parser = BaseParser()

PARSERS_MAPPING = {
    '.json': JSONParser,
    '.yml': YAMLParser,
    '.yaml': YAMLParser,
    '.xml': XMLParser,
    '.properties': PropertyParser,
    '.txt': TextParser,
    # '': TextParser, TODO: think about how to parse files without extension
}
