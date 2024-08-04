import functools
from pathlib import Path

from django_tools.unittest_utils.assertments import assert_is_file


FIXTURES_PATH = Path(__file__).parent


@functools.cache
def get_fixture_path(file_name):
    file_path = FIXTURES_PATH / file_name
    assert_is_file(file_path)
    return file_path


@functools.cache
def fixture_content(file_name, mode='rb'):
    file_path = get_fixture_path(file_name)
    with file_path.open(mode) as f:
        return f.read()
