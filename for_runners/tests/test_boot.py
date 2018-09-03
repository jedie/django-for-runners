import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from pprint import pprint

# https://github.com/jedie/django-for-runners
import for_runners
from for_runners import __version__, cli


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
    assert path.is_file(), "File '%s' not exist!" % path


def assert_is_dir(path):
    assert path.is_dir(), "Direcotry '%s' not exist!" % path


class CLITest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.cli_file_path = Path(cli.__file__)

    def test_cli_executable(self):
        assert_is_file(self.cli_file_path)
        self.assertTrue(os.access(str(self.cli_file_path), os.X_OK), "File '%s' not executeable!" % self.cli_file_path)

    def test_version(self):
        output = subprocess_output(["%s" % self.cli_file_path, "--version"])
        self.assertEqual(output, "%s\n" % __version__)

    def test_help(self):
        output = subprocess_output(["%s" % self.cli_file_path, "--help"])
        self.assertIn("Just start this file without any arguments to run the dev. server", output)


class BootTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.boot_file_path = Path(Path(for_runners.__file__).parent.parent, "boot_django_for_runners.sh")

    def test_boot_executable(self):
        assert_is_file(self.boot_file_path)
        self.assertTrue(
            os.access(str(self.boot_file_path), os.X_OK), "File '%s' not executeable!" % self.boot_file_path
        )

    def test_boot(self):
        env = os.environ.copy()

        cache_dir = Path("/home/travis/.cache/pip") # reuse pip cache from Travis CI
        if not cache_dir.is_dir():
            # Not on travis CI: Actually only important when developing,
            # we make the pip cache directory "permanent" if tests runs often ;)
            temp_dir = tempfile.gettempdir()
            cache_dir = Path(temp_dir, ".cache")
            cache_dir.mkdir(mode=0o777, parents=True, exist_ok=True)

        with tempfile.TemporaryDirectory(prefix="for_runners_test_boot_") as temp_path:

            # symlink the .cache directory into e.g.: /tmp/for_runners_test_boot_XXXXX/.cache
            cache_dir_inner = Path(temp_path, ".cache")
            self.assertFalse(cache_dir_inner.is_dir(), "Already exists: %s" % cache_dir_inner)
            cache_dir_inner.symlink_to(cache_dir, target_is_directory=True)
            self.assertTrue(cache_dir_inner.exists(), "Don't exists: %s" % cache_dir_inner)


            if "TRAVIS" in os.environ:
                # work-a-round for Travic-CI #8589, see:
                # https://github.com/travis-ci/travis-ci/issues/8589#issuecomment-372947199
                env["PATH"] = "/opt/python/3.6/bin/:%s" % env["PATH"]

            env["HOME"] = temp_path
            env["TERM"] = "dumb"
            # pprint(env)

            output = subprocess_output(["%s" % self.boot_file_path], env=env)

            env_path = Path(temp_path, "Django-ForRunners")
            assert_is_dir(env_path)

            self.assertIn(
                "+ pip3 install -e git+https://github.com/jedie/django-for-runners.git@master#egg=django-for-runners",
                output
            )
            self.assertIn(
                "+ pip3 install -r %s/Django-ForRunners/src/django-for-runners/requirements.txt" % temp_path, output
            )
            self.assertIn("+ ./for_runners --version", output)
            self.assertIn("%s" % __version__, output)

            bin_path = Path(env_path, "bin")
            assert_is_dir(bin_path)
            # subprocess_output(["ls", "-la", "%s" % bin_path], env=env)

            pip_path = Path(bin_path, "pip3")
            assert_is_file(pip_path)

            output = subprocess_output(["%s" % pip_path, "freeze"], env=env)
            self.assertIn("Django==2.1", output)
            self.assertIn("#egg=django_for_runners", output)

            manage_path = Path(bin_path, "manage")
            assert_is_file(manage_path)

            for_runners_path = Path(bin_path, "for_runners")
            assert_is_file(for_runners_path)

            output = subprocess_output(["%s" % for_runners_path, "--version"], env=env)
            self.assertIn(__version__, output)
