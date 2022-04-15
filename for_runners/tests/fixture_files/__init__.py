from pathlib import Path

from django_tools.unittest_utils.assertments import assert_is_file


FIXTURES_PATH = Path(__file__).parent


def fixture_content(file_name, mode='rb'):
    file_path = FIXTURES_PATH / file_name
    assert_is_file(file_path)
    with file_path.open(mode) as f:
        return f.read()
