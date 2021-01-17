import os
import shutil
import subprocess
from pathlib import Path

from creole.setup_utils import update_rst_readme
from django.conf import settings
from django.core.cache import cache
from django.test import TestCase

import for_runners


PACKAGE_ROOT = Path(for_runners.__file__).parent.parent.parent


def assert_file_contains_string(file_path, string):
    with file_path.open('r') as f:
        for line in f:
            if string in line:
                return
    raise AssertionError(f'File {file_path} does not contain {string!r} !')


def test_version(package_root=None, version=None):
    if package_root is None:
        package_root = PACKAGE_ROOT

    if version is None:
        version = for_runners.__version__

    if 'dev' not in version and 'rc' not in version:
        version_string = f'v{version}'

        assert_file_contains_string(
            file_path=Path(package_root, 'README.creole'),
            string=version_string
        )

        assert_file_contains_string(
            file_path=Path(package_root, 'README.rst'),
            string=version_string
        )

    assert_file_contains_string(
        file_path=Path(package_root, 'pyproject.toml'),
        string=f'version = "{version}"'
    )

    assert_file_contains_string(
        file_path=Path(package_root, 'deployment', 'project.env'),
        string=f'PROJECT_VERSION={version}'
    )


def test_poetry_check(package_root=None):
    if package_root is None:
        package_root = PACKAGE_ROOT

    poerty_bin = shutil.which('poetry')

    output = subprocess.check_output(
        [poerty_bin, 'check'],
        universal_newlines=True,
        env=os.environ,
        stderr=subprocess.STDOUT,
        cwd=str(package_root),
    )
    print(output)
    assert output == 'All set!\n'


def test_update_rst_readme(capsys):
    rest_readme_path = update_rst_readme(
        package_root=PACKAGE_ROOT, filename='README.creole'
    )
    captured = capsys.readouterr()
    assert captured.out == 'Generate README.rst from README.creole...nothing changed, ok.\n'
    assert captured.err == ''
    assert isinstance(rest_readme_path, Path)
    assert str(rest_readme_path).endswith('/README.rst')


class ProjectSettingsTestCase(TestCase):
    def test_project_path(self):
        project_path = settings.PROJECT_PATH
        assert project_path.is_dir()
        assert Path(project_path, 'for_runners').is_dir()
        assert Path(project_path, 'for_runners_project').is_dir()

    def test_template_dirs(self):
        assert len(settings.TEMPLATES) == 1
        dirs = settings.TEMPLATES[0].get('DIRS')
        assert len(dirs) == 1
        template_path = Path(dirs[0]).resolve()
        assert template_path.is_dir()

    def test_cache(self):
        # django cache should work in tests, because some tests "depends" on it
        cache_key = 'a-cache-key'
        assert cache.get(cache_key) is None
        cache.set(cache_key, 'the cache content', timeout=1)
        assert cache.get(cache_key) == 'the cache content'
        cache.delete(cache_key)
        assert cache.get(cache_key) is None
