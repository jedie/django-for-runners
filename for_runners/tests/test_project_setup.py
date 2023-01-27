import subprocess
from pathlib import Path
from unittest import TestCase

import tomli
from bx_py_utils.path import assert_is_file
from manageprojects.test_utils.click_cli_utils import subprocess_cli
from manageprojects.utilities import code_style

from for_runners import __version__
from for_runners.cli.cli_app import PACKAGE_ROOT


class ProjectSetupTestCase(TestCase):
    def test_version(self):
        pyproject_toml_path = Path(PACKAGE_ROOT, 'pyproject.toml')
        assert_is_file(pyproject_toml_path)

        self.assertIsNotNone(__version__)

        pyproject_toml = tomli.loads(pyproject_toml_path.read_text(encoding='UTF-8'))
        pyproject_version = pyproject_toml['project']['version']

        self.assertEqual(__version__, pyproject_version)

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
