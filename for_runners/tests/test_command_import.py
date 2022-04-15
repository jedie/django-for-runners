from pathlib import Path

import requests_mock
from django.core.management import call_command
from django.test import TestCase
from django_tools.unittest_utils.assertments import assert_is_dir, assert_pformat_equal
from django_tools.unittest_utils.stdout_redirect import StdoutStderrBuffer
from django_tools.unittest_utils.user import TestUserMixin
from override_storage import locmem_stats_override_storage

import for_runners
from for_runners.management.commands import import_gpx
from for_runners.models import GpxModel
from for_runners.tests.fixtures.metaweather import (
    MetaWeather4695_744Fixtures,
    MetaWeather5144_662Fixtures,
    MetaWeather5252_1338Fixtures,
    MetaWeather648820_2018_2_21Fixtures,
)
from for_runners.tests.fixtures.openstreetmap import OpenStreetMap51437889_66617012Fixtures
from for_runners.tests.utils import ClearCacheMixin


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


class ImportTestCase(TestUserMixin, ClearCacheMixin, TestCase):
    def test_import(self):
        test_username = "normal_test_user"

        assert GpxModel.objects.filter(tracked_by__username=test_username).count() == 0

        base_path = Path(for_runners.__file__).parent
        fixture_files_path = Path(base_path, "tests/fixture_files")
        assert_is_dir(fixture_files_path)

        with StdoutStderrBuffer() as buff, locmem_stats_override_storage() as storage_stats, requests_mock.mock() as m:  # noqa
            m.get(**MetaWeather5144_662Fixtures().get_requests_mock_kwargs())
            m.get(**MetaWeather648820_2018_2_21Fixtures().get_requests_mock_kwargs())
            m.get(**MetaWeather5252_1338Fixtures().get_requests_mock_kwargs())
            m.get(
                'https://www.metaweather.com/api/location/638242/2011/1/13/',
                json=[],  # No weather data
            )
            m.get(**MetaWeather4695_744Fixtures().get_requests_mock_kwargs())
            m.get(
                'https://www.metaweather.com/api/location/784794/2011/1/15/',
                json=[],  # No weather data
            )
            m.get(
                (
                    'https://nominatim.openstreetmap.org/reverse'
                    '?lat=0.0&lon=180.0&format=json&addressdetails=1&zoom=17'
                ),
                json={"error": "Unable to geocode"},
            )
            m.get(**OpenStreetMap51437889_66617012Fixtures().get_requests_mock_kwargs())

            call_command(import_gpx.Command(), "--username", test_username, str(fixture_files_path))
            assert storage_stats.fields_saved == [
                ('for_runners', 'gpxmodel', 'track_svg'),
                ('for_runners', 'gpxmodel', 'gpx_file'),
            ]
            assert storage_stats.fields_read == []

            output = buff.get_output()
            print(output)

            self.assertIn("Add new gpx tracks for user: normal_test_user", output)
            self.assertIn("1 - Add new track: 2018-02-21", output)
            self.assertIn("2 - Add new track: 2011-01-13", output)
            self.assertIn("Added 2 new gpx tracks.", output)
            self.assertIn("User normal_test_user has now 2 tracks.", output)

            qs = GpxModel.objects.filter(tracked_by__username=test_username)

            existing_tracks = [str(track) for track in qs]
            assert_pformat_equal(existing_tracks, ['2018-02-21', '2011-01-13'])

            assert qs.count() == 2
            assert storage_stats.fields_read == []
