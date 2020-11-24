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
from for_runners.tests.fixture_files import fixture_content
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

        with StdoutStderrBuffer() as buff, \
                locmem_stats_override_storage() as storage_stats, \
                requests_mock.mock() as m:
            m.get(
                'https://www.metaweather.com/api/location/search/?lattlong=51.44,6.62',
                headers={'Content-Type': 'application/json'},
                content=fixture_content('metaweather_5144_662.json')
            )
            m.get(
                'https://www.metaweather.com/api/location/648820/2018/2/21/',
                headers={'Content-Type': 'application/json'},
                content=fixture_content('metaweather_location_648820_2018_2_21.json')
            )
            m.get(
                'https://www.metaweather.com/api/location/search/?lattlong=52.52,13.38',
                headers={'Content-Type': 'application/json'},
                content=fixture_content('metaweather_5252_1338.json')  # 4.5°C 'Light Cloud'
            )
            m.get(
                'https://www.metaweather.com/api/location/638242/2011/1/13/',
                headers={'Content-Type': 'application/json'},
                content=b'[]',  # No weather data for start.
            )
            m.get(
                'https://www.metaweather.com/api/location/search/?lattlong=46.95,7.44',
                headers={'Content-Type': 'application/json'},
                content=fixture_content('metaweather_4695_744.json')
            )
            m.get(
                'https://www.metaweather.com/api/location/784794/2011/1/15/',
                headers={'Content-Type': 'application/json'},
                content=b'[]',  # No weather data for start.
            )
            m.get(
                (
                    'https://nominatim.openstreetmap.org/reverse'
                    '?lat=0.0&lon=0.0&format=json&addressdetails=1&zoom=17'
                ),
                headers={'Content-Type': 'application/json'},
                content=fixture_content('nominatim_osm_reverse_0_0.json')
            )
            m.get(
                (
                    'https://nominatim.openstreetmap.org/reverse'
                    '?lat=0.0&lon=180.0&format=json&addressdetails=1&zoom=17'
                ),
                headers={'Content-Type': 'application/json'},
                content=b'{"error":"Unable to geocode"}'
            )
            m.get(
                (
                    'https://nominatim.openstreetmap.org/reverse'
                    '?lat=51.437889290973544&lon=6.617012657225132&format=json&addressdetails=1&zoom=17'
                ),
                headers={'Content-Type': 'application/json'},
                content=fixture_content('nominatim_osm_reverse_0_0.json')
            )
            call_command(import_gpx.Command(), "--username", test_username, str(fixture_files_path))
            assert storage_stats.fields_saved == [
                ('for_runners', 'gpxmodel', 'track_svg'),
                ('for_runners', 'gpxmodel', 'gpx_file')
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
            assert_pformat_equal(
                existing_tracks, ['2018-02-21', '2011-01-13']
            )

            assert qs.count() == 2
            assert storage_stats.fields_read == []
