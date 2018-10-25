#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function

import fnmatch
import os
import yaml

from collections import OrderedDict

from shaper import lib
from shaper.lib.configi import FILE_TYPES

from jinja2 import Environment, FileSystemLoader


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
        loader=FileSystemLoader(
            os.path.dirname(template_path)
        )
    )
    env.globals.update(context)
    template = env.get_template(os.path.basename(template_path))
    return template.render()


def merge_templates(rendered_templates, template_dir):
    dict_base = {}
    for var in rendered_templates:
        dict_base.update(yaml.safe_load(var))
    with open(os.path.join(template_dir, 'templates.yaml'), 'w') as f:
        yaml.dump(dict_base, f, default_flow_style=False)

