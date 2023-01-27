from bx_py_utils.path import assert_is_file
from django.core.management import call_command
from django.test import SimpleTestCase
from django_tools.unittest_utils.project_setup import check_editor_config

from manage_django_project.config import manage_config
from manage_django_project.management.commands import code_style


def assert_file_contains_string(file_path, string):
    assert_is_file(file_path)
    with file_path.open('r') as f:
        for line in f:
            if string in line:
                return
    raise AssertionError(f'File {file_path} does not contain {string!r} !')


class ProjectSettingsTestCase(SimpleTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        manage_config.assert_initialized()

    def test_version(self):
        self.assertIsNotNone(manage_config.module.__version__)

        pyproject_toml = manage_config.get_pyproject_toml()
        pyproject_version = pyproject_toml['project']['version']

        self.assertEqual(manage_config.module.__version__, pyproject_version)

        assert_file_contains_string(file_path=manage_config.readme_path, string=pyproject_version)

    def test_check_editor_config(self):
        check_editor_config(package_root=manage_config.base_path)

    def test_code_style(self):
        # Just run our django manage command that call's darker and flake8

        try:
            call_command(code_style.Command())
        except SystemExit as err:
            if err.code != 0:
                self.fail('Code style errors, see above!')
