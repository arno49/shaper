import os
import shutil
from collections import OrderedDict

from shaper import manager, libs


def test_create_folder():
    temp_dir_name = 'test_folder'
    manager.create_folders(temp_dir_name)
    assert os.path.isdir(temp_dir_name)
    shutil.rmtree(temp_dir_name)


def test_read_properties(test_assets_root):
    input_dir = test_assets_root / 'input'
    filename_data_map = manager.read_properties(input_dir)

    for filename, data in filename_data_map.items():
        assert os.path.splitext(filename)[1] in libs.PARSERS_MAPPING
        assert data is not None
        # assert isinstance(data, (dict, OrderedDict)) # commented until https://github.com/arno49/shaper/issues/41 is not fully fixed


def test_forward_path_parser():
    datastructure = {
        'g/e/c6': 'c6',
        'a/d/c3': 'c3',
        'a/b/c1': 'c1',
        'a/c4': 'c4',
        'a/b/c2': 'c2',
        'g/c5': 'c5',
    }

    expected = {
        'a': {
            'b': {'c1': 'c1', 'c2': 'c2'},
            'c4': 'c4',
            'd': {'c3': 'c3'},
        },
        'g': {
            'c5': 'c5',
            'e': {'c6': 'c6'},
        },
    }

    assert expected == manager.forward_path_parser(datastructure)


def test_backward_path_parser():
    datastructure = OrderedDict(
        [
            (
                'a',
                OrderedDict(
                    [
                        ('c4.py', 'c4'),
                        ('d', OrderedDict([('c3.py', 'c3')])),
                        ('b', OrderedDict([('c2.py', 'c2'), ('c1.py', 'c1')])),
                    ],
                ),
            ),
            ('g', OrderedDict([('c5.py', 'c5'), ('e', OrderedDict([('c6.py', 'c6')]))])),
        ],
    )

    expected = {
        'a/b/c1.py': 'c1',
        'a/b/c2.py': 'c2',
        'a/c4.py': 'c4',
        'a/d/c3.py': 'c3',
        'g/c5.py': 'c5',
        'g/e/c6.py': 'c6',
    }

    assert expected == manager.backward_path_parser(datastructure)

