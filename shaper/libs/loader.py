from collections import OrderedDict

import yaml
from yaml.constructor import ConstructorError


class OrderedDictYAMLLoader(yaml.Loader):  # pylint: disable=too-many-ancestors
    """
    A YAML loader that loads mappings into ordered dictionaries.
    """

    def __init__(self, *args, **kwargs):
        yaml.Loader.__init__(self, *args, **kwargs)

        OrderedDictYAMLLoader.add_constructor(
            u'tag:yaml.org,2002:map',
            OrderedDictYAMLLoader.construct_yaml_map,
        )
        OrderedDictYAMLLoader.add_constructor(
            u'tag:yaml.org,2002:omap',
            OrderedDictYAMLLoader.construct_yaml_map,
        )

    def construct_yaml_map(self, node):
        data = OrderedDict()
        yield data
        value = self.construct_mapping(node)
        data.update(value)

    def construct_mapping(self, node, deep=False):
        if isinstance(node, yaml.MappingNode):
            self.flatten_mapping(node)
        else:
            raise ConstructorError(
                None,
                None,
                'expected a mapping node, but found %s' % node.id,
                node.start_mark,
            )

        mapping = OrderedDict()
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            try:
                hash(key)
            except TypeError as exc:
                raise ConstructorError(
                    'while constructing a mapping',
                    node.start_mark,
                    'found unacceptable key (%s)' % exc, key_node.start_mark,
                )
            value = self.construct_object(value_node, deep=deep)
            mapping[key] = value
        return mapping


def represent_ordered_dict(dumper, data):
    """Function for Ordered Dictionary representation."""

    value = []

    for item_key, item_value in data.items():
        node_key = dumper.represent_data(item_key)
        node_value = dumper.represent_data(item_value)

        value.append((node_key, node_value))

    return yaml.nodes.MappingNode(u'tag:yaml.org,2002:map', value)


def represent_unicode(dumper, _unicode):  # pylint: disable=unused-argument
    """Function for unicode representation."""

    return yaml.ScalarNode(u'tag:yaml.org,2002:str', _unicode)


# string representer for multi line issue
def represent_multi_line(dumper, data):
    style = None
    if len(data.splitlines()) > 1:  # check for multi line string
        style = '|'
    return dumper.represent_scalar('tag:yaml.org,2002:str', data, style=style)
