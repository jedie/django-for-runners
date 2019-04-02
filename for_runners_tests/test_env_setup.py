import shutil
from pathlib import Path
from unittest import TestCase

from django import __version__ as django_version

# https://github.com/jedie/django-tools
from django_tools.unittest_utils.assertments import assert_endswith
from django_tools.unittest_utils.django_command import DjangoCommandMixin

# https://github.com/jedie/django-for-runners
from for_runners.version import __version__


class CheckTestEnvironment(DjangoCommandMixin, TestCase):
    @classmethod
    def setUpClass(cls):
        # installed via setup.py entry points !
        cls.for_runners_bin = shutil.which("for_runners")
        cls.manage_bin = shutil.which("manage")

    def test_for_runners_path(self):
        assert_endswith(text=self.for_runners_bin, suffix="/bin/for_runners")

    def test_manage_bin(self):
        assert_endswith(text=self.manage_bin, suffix="/bin/manage")

    def _call_for_runners(self, cmd):
        for_runners_path = Path(self.for_runners_bin)
        return self.call_manage_py(
            cmd=cmd, manage_dir=str(for_runners_path.parent), manage_py=for_runners_path.name  # Python 3.5 needs str()
        )

    def test_for_runners_version(self):
        self.assertEqual(self._call_for_runners(["--version"]), "Django-ForRunners, version %s" % __version__)

    def test_for_runners_help(self):
        output = self._call_for_runners(["--help"])
        self.assertIn("Usage: for_runners [OPTIONS] COMMAND [ARGS]...", output)
        self.assertIn("backup", output)
        self.assertIn("create-starter", output)
        self.assertIn("run-dev-server", output)
        self.assertIn("update", output)

    def _call_manage(self, cmd):
        manage_path = Path(self.manage_bin)
        return self.call_manage_py(
            cmd=cmd, manage_dir=str(manage_path.parent), manage_py=manage_path.name  # Python 3.5 needs str()
        )

    def test_manage_version(self):
        output = self._call_manage(["--version"])
        print(output)
        self.assertIn(django_version, output)

    def test_manage_help(self):
        output = self._call_manage(["--help"])
        print(output)
        self.assertIn("Available subcommands:", output)
        self.assertIn("[django]", output)
        self.assertIn("[for_runners]", output)
        self.assertIn("import_gpx", output)
        self.assertIn("[for_runners_helper_app]", output)
        self.assertIn("run_server", output)

    def test_manage_check(self):
        output = self._call_manage(["check"])
        print(output)
        self.assertIn("System check identified no issues (0 silenced).", output)

    def test_update(self):
        output = self._call_for_runners(["update"])
        print(output)
        self.assertIn("git pull", output)
        self.assertIn("pip3 install --upgrade pip", output)
        self.assertIn("pip3 install --upgrade -r", output)
        self.assertIn("Your virtual environment is updated!", output)
