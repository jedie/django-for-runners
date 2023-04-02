from pathlib import Path
import subprocess
from unittest import TestCase

from django.conf import settings
from django.core.cache import cache
from bx_py_utils.path import assert_is_file
from manageprojects.test_utils.click_cli_utils import subprocess_cli
from manageprojects.test_utils.project_setup import check_editor_config, get_py_max_line_length
from manageprojects.utilities import code_style
from packaging.version import Version

from for_runners import __version__
from for_runners.cli.cli_app import PACKAGE_ROOT


class ProjectSetupTestCase(TestCase):
    def test_project_path(self):
        project_path = settings.BASE_PATH
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

    def test_settings(self):
        self.assertEqual(settings.SETTINGS_MODULE, 'for_runners_project.settings.tests')
        middlewares = [entry.rsplit('.', 1)[-1] for entry in settings.MIDDLEWARE]
        assert 'AlwaysLoggedInAsSuperUserMiddleware' not in middlewares
        assert 'DebugToolbarMiddleware' not in middlewares
    def test_version(self):
        self.assertIsNotNone(__version__)

        version = Version(__version__)  # Will raise InvalidVersion() if wrong formatted
        self.assertEqual(str(version), __version__)

        cli_bin = PACKAGE_ROOT / 'cli.py'
        assert_is_file(cli_bin)

        output = subprocess.check_output([cli_bin, 'version'], text=True)
        self.assertIn(f'for_runners v{__version__}', output)

    def test_code_style(self):
        cli_bin = PACKAGE_ROOT / 'cli.py'
        assert_is_file(cli_bin)

        try:
            output = subprocess_cli(
                cli_bin=cli_bin,
                args=('check-code-style',),
                exit_on_error=False,
            )
        except subprocess.CalledProcessError as err:
            self.assertIn('.venv/bin/darker', err.stdout)  # darker was called?
        else:
            if 'Code style: OK' in output:
                self.assertIn('.venv/bin/darker', output)  # darker was called?
                return  # Nothing to fix -> OK

        # Try to "auto" fix code style:

        try:
            output = subprocess_cli(
                cli_bin=cli_bin,
                args=('fix-code-style',),
                exit_on_error=False,
            )
        except subprocess.CalledProcessError as err:
            output = err.stdout

        self.assertIn('.venv/bin/darker', output)  # darker was called?

        # Check again and display the output:

        try:
            code_style.check(package_root=PACKAGE_ROOT)
        except SystemExit as err:
            self.assertEqual(err.code, 0, 'Code style error, see output above!')

    def test_check_editor_config(self):
        check_editor_config(package_root=PACKAGE_ROOT)

        max_line_length = get_py_max_line_length(package_root=PACKAGE_ROOT)
        self.assertEqual(max_line_length, 119)
