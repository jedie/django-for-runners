import shutil
import unittest
from pathlib import Path
from unittest.mock import patch

from django import __version__ as django_version
from django.core.management import call_command
from django.test import TestCase
# https://github.com/jedie/django-tools
from django_tools.unittest_utils.assertments import assert_endswith, assert_is_dir, assert_pformat_equal
from django_tools.unittest_utils.django_command import DjangoCommandMixin
from django_tools.unittest_utils.stdout_redirect import StdoutStderrBuffer
from django_tools.unittest_utils.user import TestUserMixin

# https://github.com/jedie/django-for-runners
import for_runners
from for_runners import __version__
from for_runners.models import GpxModel
from for_runners.tests.base import BaseTestCase
from for_runners_tests.utils import ForRunnersCommandTestCase


# TODO:
# class ImportCommandTestCase(ForRunnersCommandTestCase):
#     def test_in_help(self):
#         output = self._call_manage(["--help"])
#         print(output)
#         self.assertIn("Available subcommands:", output)
#         self.assertIn("[for_runners]", output)
#         self.assertIn("import_gpx", output)
#
#     def test_import_help(self):
#         output = self._call_manage(["import_gpx", "--help"])
#         print(output)
#         self.assertIn("usage: manage import_gpx", output)
#         self.assertIn("Path to *.gpx files", output)
#
#     def test_import_no_username_given(self):
#         output = self._call_manage(["import_gpx", "/foo/bar"], excepted_exit_code=2)
#         print(output)
#         self.assertIn("following arguments are required: --username", output)
#
#     def test_import_wrong_username(self):
#         output = self._call_manage(
#             ["import_gpx", "--username", "NotExistingUser", "/foo/bar"], excepted_exit_code=3
#         )
#         print(output)
#         self.assertIn("ERROR getting user 'NotExistingUser'", output)
#         self.assertIn("Existing usernames are", output)
#         self.assertIn("test", output)
#
#     def test_import_wrong_path(self):
#         output = self._call_manage(
#             ["import_gpx", "--username", "test", "/foo/bar"], excepted_exit_code=4
#         )
#         print(output)
#         self.assertIn("ERROR: Given path '/foo/bar' is not a existing directory!", output)


class ImportTestCase(TestUserMixin, TestCase):
    def test_import(self):
        test_username = "normal_test_user"

        assert GpxModel.objects.filter(tracked_by__username=test_username).count() == 0

        base_path = Path(for_runners.__file__).parent
        fixture_files_path = Path(base_path, "tests/fixture_files")
        assert_is_dir(fixture_files_path)

        with StdoutStderrBuffer() as buff:
            with patch(
                "for_runners.services.gpx_calculate_values.meta_weather_com.coordinates2weather",
                return_value=(27.94, "Light Cloud"),
            ):
                call_command("import_gpx", "--username", test_username, str(fixture_files_path))

        output = buff.get_output()
        print(output)

        self.assertIn("Add new gpx tracks for user: normal_test_user", output)
        self.assertIn("1 - Add new track: 2018-02-21 Moers", output)
        self.assertIn("2 - Add new track: 2011-01-13 Berlin Tiergarten", output)
        self.assertIn("Added 2 new gpx tracks.", output)
        self.assertIn("User normal_test_user has now 2 tracks.", output)

        qs = GpxModel.objects.filter(tracked_by__username=test_username)

        existing_tracks = [str(track) for track in qs]
        assert_pformat_equal(
            existing_tracks, ["2018-02-21 Moers", "2011-01-13 Berlin Tiergarten"]
        )

        assert qs.count() == 2
