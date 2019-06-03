#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""shaper renderer - tools to working with templates"""
from __future__ import print_function

import os
from collections import OrderedDict
import yaml

from jinja2 import Environment, FileSystemLoader, Undefined
from . import manager


class IgnoreUndefinedAttr(Undefined):  # pylint: disable=too-few-public-methods
    """
    Class for ignoring undefined attributes
    """
    def __getattr__(self, name):
        return None


# override default behavior of representing empty string as None object in Jinja2
# empty string will be returned as empty string (not as None object)
# def represent_none_as_empty_string(value):
#     if value is None:
#         return ""
#     return value


def render_template(template_path, context):
    """
    Render template interface

    :param template_path: path to template
    :type template_path: str

    :param context: variables
    :type context: dict

    :return: rendered template
    :rtype: str
    """

    env = Environment(
        loader=FileSystemLoader(os.path.dirname(template_path)),
        undefined=IgnoreUndefinedAttr
        # finalize=represent_none_as_empty_string
    )
    env.globals.update(context)
    template = env.get_template(os.path.basename(template_path))
    return template.render()


def merge_templates(rendered_templates, out_dir):
    """
    Merge templates

    :param rendered_templates: list of rendered templates to merge

    :param out_dir: path to rendered property files

    :return: None
    """
    datastructure = {}
    for var in rendered_templates:
        datastructure.update(yaml.safe_load(var))

    datastructure = manager.backward_path_parser(datastructure)
    for key in datastructure:
        datastructure[key] = OrderedDict((k, v) for k, v in sorted(datastructure[key].items()))
    manager.write_properties(datastructure, out_dir)
