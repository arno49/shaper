#!/usr/bin/env python
# coding: utf-8

"""
Converts a Python dictionary or other native data type into a valid XML string.

Supports item (`int`, `float`, `long`, `decimal.Decimal`, `bool`, `str`,
`unicode`, `datetime`, `none` and other number-like objects) and collection
(`list`, `set`, `tuple` and `dict`, as well as iterable and dict-like objects)
data types, with arbitrary nesting for the collections. Items with a `datetime`
 type are converted to ISO format strings. Items with a `None` type become
 empty XML elements.
"""

import collections
import logging
import numbers
from random import randint
from xml.dom.minidom import parseString

try:
    unicode, long
except NameError:
    unicode = str  # pylint: disable=redefined-builtin
    long = int  # pylint: disable=redefined-builtin

logger = logging.getLogger("dicttoxml")


def set_debug(debug=True, filename='dicttoxml.log'):
    if debug:
        import datetime
        logging.basicConfig(filename=filename, level=logging.INFO)
        logger.info('\nLogging session starts: %s', datetime.datetime.today())
    else:
        logging.basicConfig(level=logging.WARNING)


def unicode_me(something):
    """Converts strings with non-ASCII characters to unicode for logger.
    Python 3 doesn't have a `unicode()` function, so `unicode()` is an alias
    for `str()`, but `str()` doesn't take a second argument, hence this kludge.
    """
    try:
        return unicode(something, 'utf-8')
    except TypeError:
        return unicode(something)


def make_id(element, start=100000, end=999999):
    """Returns a random integer"""
    return '%s_%s' % (element, randint(start, end))


def get_unique_id(element):
    """Returns a unique id for a given element"""
    ids = []
    this_id = make_id(element)
    dup = True
    while dup:
        if this_id not in ids:
            dup = False
            ids.append(this_id)
        else:
            this_id = make_id(element)
    return ids[-1]


def get_xml_type(val):
    """Returns the data type for the xml type attribute"""
    if isinstance(val, (str, unicode)):
        return 'str'
    if isinstance(val, (int, long)):
        return 'int'
    if isinstance(val, float):
        return 'float'
    if isinstance(val, bool):
        return 'bool'
    if isinstance(val, numbers.Number):
        return 'number'
    if val is None:
        return 'null'
    if isinstance(val, dict):
        return 'dict'
    if isinstance(val, collections.Iterable):
        return 'list'

    return type(val).__name__


def escape_xml(s):
    if isinstance(s, (str, unicode)):
        s = unicode_me(s)  # avoid UnicodeDecodeError
        s = s.replace('&', '&amp;')
        s = s.replace('"', '&quot;')
        s = s.replace('\'', '&apos;')
        s = s.replace('<', '&lt;')
        s = s.replace('>', '&gt;')

    return s


def make_attr_string(attr):
    """Returns an attribute string in the form key="val"."""
    attr_string = ' '.join('%s="%s"' % (k, v) for k, v in attr.items())
    return '%s%s' % (' ' if attr_string != '' else '', attr_string)


def key_is_valid_xml(key):
    """Checks that a key is a valid XML name"""
    logger.info('Inside key_is_valid_xml(). Testing "%s"', unicode_me(key))
    test_xml = '<?xml version="1.0" encoding="UTF-8" ?><%s>foo</%s>' % (key, key)
    try:
        parseString(test_xml)
        return True
    except Exception:  # pylint: disable=broad-except
        return False


def make_valid_xml_name(key, attr):
    """Tests an XML name and fixes it if invalid"""
    logger.info(
        'Inside make_valid_xml_name(). Testing key "%s" with attr "%s"',
        unicode_me(key), unicode_me(attr),
    )
    key = escape_xml(key)
    attr = escape_xml(attr)

    # pass through if key is already valid
    if key_is_valid_xml(key):
        return key, attr

    # prepend a lowercase n if the key is numeric
    if key.isdigit():
        return 'n%s' % (key), attr

    # replace spaces with underscores if that fixes the problem
    if key_is_valid_xml(key.replace(' ', '_')):
        return key.replace(' ', '_'), attr

    # key is still invalid - move it into a name attribute
    attr['name'] = key
    key = 'key'
    return key, attr


def wrap_cdata(s):
    """Wraps a string into CDATA sections"""
    s = unicode_me(s).replace(']]>', ']]]]><![CDATA[>')
    return '<![CDATA[' + s + ']]>'


def convert(obj, ids, attr_type, item_func, cdata, fold_list, parent='root'):
    """Routes the elements of an object to the right function to convert them
    based on their data type"""

    logger.info(
        'Inside convert(). obj type is: "%s", obj="%s"',
        type(obj).__name__, unicode_me(obj),
    )

    item_name = item_func(parent)

    if isinstance(obj, (numbers.Number, str, unicode)):
        return convert_kv(item_name, obj, attr_type, cdata)

    if hasattr(obj, 'isoformat'):
        return convert_kv(item_name, obj.isoformat(), attr_type, cdata)

    if isinstance(obj, bool):
        return convert_bool(item_name, obj, attr_type)

    if obj is None:
        return convert_none(item_name, '', attr_type)

    if isinstance(obj, dict):
        return convert_dict(
            obj, ids, parent, attr_type, item_func, cdata, fold_list)

    if isinstance(obj, collections.Iterable):
        return convert_list(
            obj, ids, parent, attr_type, item_func, cdata, fold_list)

    raise TypeError(
        'Unsupported data type: %s (%s)' % (obj, type(obj).__name__))


def convert_dict(obj, ids, parent, attr_type, item_func, cdata, fold_list):
    """Converts a dict into an XML string."""
    logger.info(
        'Inside convert_dict(): obj type is: "%s", obj="%s"',
        type(obj).__name__, unicode_me(obj),
    )

    output = []
    for key, val in obj.items():
        logger.info(
            'Looping inside convert_dict(): key="%s", val="%s", type(val)="%s"',
            unicode_me(key), unicode_me(val), type(val).__name__,
        )

        attr = {} if not ids else {'id': get_unique_id(parent)}

        key, attr = make_valid_xml_name(key, attr)

        if isinstance(val, (numbers.Number, str, unicode)):
            output.append(convert_kv(key, val, attr_type, cdata, **attr))

        elif hasattr(val, 'isoformat'):  # datetime
            output.append(
                convert_kv(key, val.isoformat(), attr_type, cdata, **attr),
            )

        elif isinstance(val, bool):
            output.append(convert_bool(key, val, attr_type, **attr))

        elif isinstance(val, dict):
            if attr_type:
                attr['type'] = get_xml_type(val)

            output.append(
                '<%s%s>%s</%s>' % (
                    key,
                    make_attr_string(attr),
                    convert_dict(val, ids, key, attr_type, item_func, cdata, fold_list),
                    key,
                ),
            )

        elif isinstance(val, collections.Iterable):
            if attr_type:
                attr['type'] = get_xml_type(val)

            if fold_list:
                output.append(
                    '<%s%s>%s</%s>' % (
                        key,
                        make_attr_string(attr),
                        convert_list(val, ids, key, attr_type, item_func, cdata, fold_list),
                        key,
                    ),
                )
            else:
                output.append(
                    convert_list(val, ids, key, attr_type, item_func, cdata, fold_list),
                )

        elif val is None:
            output.append(convert_none(key, val, attr_type, **attr))

        else:
            raise TypeError(
                'Unsupported data type: %s (%s)' % (val, type(val).__name__),
            )

    return ''.join(output)


def convert_list(items, ids, parent, attr_type, item_func, cdata, fold_list):
    """Converts a list into an XML string."""
    logger.info('Inside convert_list()')

    if fold_list:
        item_name = item_func(parent)
    else:
        item_name = parent

    output = []
    for i, item in enumerate(items):
        logger.info(
            'Looping inside convert_list(): item="%s", item_name="%s", type="%s"',
            unicode_me(item), item_name, type(item).__name__,
        )
        attr = {} if not ids else {'id': '%s_%s' % (get_unique_id(parent), i + 1)}

        if isinstance(item, (numbers.Number, str, unicode)):
            output.append(convert_kv(item_name, item, attr_type, cdata, **attr))

        elif hasattr(item, 'isoformat'):  # datetime
            output.append(
                convert_kv(item_name, item.isoformat(), attr_type, cdata, **attr),
            )

        elif isinstance(item, bool):
            output.append(convert_bool(item_name, item, attr_type, **attr))

        elif isinstance(item, dict):
            if not attr_type:
                output.append(
                    '<%s>%s</%s>' % (
                        item_name,
                        convert_dict(item, ids, parent, attr_type, item_func, cdata, fold_list),
                        item_name,
                    ),
                )
            else:
                output.append(
                    '<%s type="dict">%s</%s>' % (
                        item_name,
                        convert_dict(item, ids, parent, attr_type, item_func, cdata, fold_list),
                        item_name,
                    ),
                )

        elif isinstance(item, collections.Iterable):
            if not attr_type:
                output.append(
                    '<%s%s>%s</%s>' % (
                        item_name,
                        make_attr_string(attr),
                        convert_list(item, ids, item_name, attr_type, item_func, cdata, fold_list),
                        item_name,
                    ),
                )
            else:
                output.append(
                    '<%s type="list"%s>%s</%s>' % (
                        item_name, make_attr_string(attr),
                        convert_list(item, ids, item_name, attr_type, item_func, cdata, fold_list),
                        item_name,
                    ),
                )

        elif item is None:
            output.append(convert_none(item_name, None, attr_type, **attr))

        else:
            raise TypeError(
                'Unsupported data type: %s (%s)' % (item, type(item).__name__),
            )

    return ''.join(output)


def convert_kv(key, val, attr_type, cdata, **attr):
    """Converts a number or string into an XML element"""
    logger.info(
        'Inside convert_kv(): key="%s", val="%s", type(val) is: "%s"',
        unicode_me(key), unicode_me(val), type(val).__name__,
    )

    key, attr = make_valid_xml_name(key, attr)

    if attr_type:
        attr['type'] = get_xml_type(val)

    attr_string = make_attr_string(attr)

    return '<%s%s>%s</%s>' % (
        key,
        attr_string,
        wrap_cdata(val) if cdata else escape_xml(val),
        key,
    )


def convert_bool(key, val, attr_type, **attr):
    """Converts a boolean into an XML element"""
    logger.info(
        'Inside convert_bool(): key="%s", val="%s", type(val) is: "%s"',
        unicode_me(key), unicode_me(val), type(val).__name__,
    )

    key, attr = make_valid_xml_name(key, attr)

    if attr_type:
        attr['type'] = get_xml_type(val)

    attr_string = make_attr_string(attr)

    return '<%s%s>%s</%s>' % (key, attr_string, unicode(val).lower(), key)


def convert_none(key, val, attr_type, **attr):
    """Converts a null value into an XML element"""
    logger.info('Inside convert_none(): key="%s"', unicode_me(key))

    key, attr = make_valid_xml_name(key, attr)

    if attr_type:
        attr['type'] = get_xml_type(val)

    attr_string = make_attr_string(attr)

    return '<%s%s></%s>' % (key, attr_string, key)


def dict_to_xml(
        obj, root=True, custom_root='root', ids=False, attr_type=True,
        item_func=lambda x: 'item', cdata=False, fold_list=True,
):
    """Converts a python object into XML.
    Arguments:
    - root specifies whether the output is wrapped in an XML root element
      Default is True
    - custom_root allows you to specify a custom root element.
      Default is 'root'
    - ids specifies whether elements get unique ids.
      Default is False
    - attr_type specifies whether elements get a data type attribute.
      Default is True
    - item_func specifies what function should generate the element name for
      items in a list.
      Default is 'item'
    - cdata specifies whether string values should be wrapped in CDATA sections.
      Default is False
    """
    logger.info(
        'Inside dict_to_xml(): type(obj) is: "%s", obj="%s"',
        type(obj).__name__, unicode_me(obj),
    )

    output = []
    if root:
        output.append('<?xml version="1.0" encoding="UTF-8" ?>')
        output.append(
            '<%s>%s</%s>' % (
                custom_root,
                convert(obj, ids, attr_type, item_func, cdata, fold_list, parent=custom_root),
                custom_root,
            ),
        )
    else:
        output.append(
            convert(obj, ids, attr_type, item_func, cdata, fold_list, parent=''),
        )

    return ''.join(output).encode('utf-8')
