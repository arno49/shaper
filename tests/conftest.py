import pytest

from shaper.utils import find_git_root


@pytest.fixture(scope='session')
def test_assets_root():
    return find_git_root(__file__) / 'tests' / 'assets'
