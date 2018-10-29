"""Unittests for shaper.manager"""
# pylint: disable=R0201

import unittest

from mock import patch

from shaper import manager


class TestManager(unittest.TestCase):
    """Test manager test cases"""
    def setUp(self):
        """setUp method"""
        pass

    def tearDown(self):
        """tearDown method"""
        pass

    @patch('os.makedirs')
    def test_create_folders_works(self, mock_make_dirs):
        """Check that manager.create_folders call create dir"""
        mock_make_dirs.return_value = True
        manager.create_folders("test_folder")
        mock_make_dirs.assert_called_with("test_folder")


if __name__ == '__main__':
    unittest.main()
