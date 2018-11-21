import os
import shutil

from shaper import manager, libs


def test_read(test_assets_root):
    """
    This test is sensitive to the input directory relative path value.
    Run it only from the project root dir.
    """
    input_dir = test_assets_root / 'input'
    output_file_path = test_assets_root / 'test_output.yml'
    expected_file_path = test_assets_root / 'expected_out.yml'

    gathered_data = manager.read_properties(input_dir.relpath())
    tree = manager.forward_path_parser(gathered_data)

    libs.parser.write(tree, output_file_path)

    output_data = libs.parser.read(output_file_path)
    output_data = manager.backward_path_parser(output_data)

    expected_data = libs.parser.read(expected_file_path)
    expected_data = manager.backward_path_parser(expected_data)

    for key, value in output_data.items():
        assert expected_data[key] == value

    os.remove(output_file_path)


def test_write(test_assets_root):
    output_dir = test_assets_root / 'output'
    input_file_path = test_assets_root / 'expected_out.yml'

    data = libs.parser.read(input_file_path)
    datastructure = manager.backward_path_parser(data)

    manager.write_properties(datastructure, output_dir)

    output_dir_listing = manager.walk_on_path(output_dir)
    expected_dir_listing = manager.walk_on_path(test_assets_root / 'input')
    for output_file, expected_file in zip(output_dir_listing, expected_dir_listing):
        output_data = libs.parser.read(output_file)
        expected_data = libs.parser.read(expected_file)

        assert output_data == expected_data

    shutil.rmtree(output_dir)


def test_play():
    pass
