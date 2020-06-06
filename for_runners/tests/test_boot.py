import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from pprint import pprint

from for_runners_project import cli

# https://github.com/jedie/django-for-runners
import for_runners
from for_runners import __version__


def subprocess_output(*args, **kwargs):
    kwargs["stderr"] = subprocess.STDOUT
    print("_" * 100)
    print("Call:", args, kwargs)
    try:
        output = subprocess.check_output(*args, **kwargs)
    except subprocess.CalledProcessError as err:
        print(err.output.decode("UTF-8"))
        raise

    output = output.decode("UTF-8")
    print(output)
    return output


def assert_is_file(path):
    assert path.is_file(), f"File '{path}' not exist!"


def assert_is_dir(path):
    assert path.is_dir(), f"Direcotry '{path}' not exist!"


class CLITest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cli_file_path = Path(cli.__file__)

    def test_cli_executable(self):
        assert_is_file(self.cli_file_path)
        self.assertTrue(os.access(str(self.cli_file_path), os.X_OK), f"File '{self.cli_file_path}' not executeable!")

    def test_version(self):
        output = subprocess_output([f"{self.cli_file_path}", "--version"])
        self.assertIn(f"version {__version__}", output)

    def test_help(self):
        output = subprocess_output([f"{self.cli_file_path}", "--help"])
        self.assertIn("Usage: cli.py [OPTIONS] COMMAND [ARGS]...", output)
        self.assertIn("create-starter", output)
        self.assertIn("run-dev-server", output)
        self.assertIn("run-server", output)
