from pathlib import Path

import requests_mock
from bx_py_utils.test_utils.snapshot import assert_snapshot
from django.core.management import call_command
from django.test import TestCase
from django_tools.unittest_utils.assertments import assert_is_dir, assert_pformat_equal
from django_tools.unittest_utils.stdout_redirect import StdoutStderrBuffer
from django_tools.unittest_utils.user import TestUserMixin
from override_storage import locmem_stats_override_storage

import for_runners
from for_runners.management.commands import import_tracks
from for_runners.models import GpxModel
from for_runners.tests.fixtures.openstreetmap import (
    OpenStreetMap00000000_00000000Fixtures,
    OpenStreetMap5105254_244456Fixtures,
    OpenStreetMap5143789_661701Fixtures,
    OpenStreetMap5251861_1337611Fixtures,
    OpenStreetMap51437889_66617012Fixtures,
)
from for_runners.tests.mocks.weather_mock import WeatherMock
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
        print('*' * 1000)
        test_username = "normal_test_user"

        assert GpxModel.objects.count() == 0

        base_path = Path(for_runners.__file__).parent
        fixture_files_path = Path(base_path, "tests/fixture_files")
        assert_is_dir(fixture_files_path)

        with (
            StdoutStderrBuffer() as buff,
            locmem_stats_override_storage() as storage_stats,
            requests_mock.mock() as m,
            WeatherMock() as weather_mock,
        ):
            m.get(
                (
                    'https://nominatim.openstreetmap.org/reverse'
                    '?lat=0.0&lon=180.0&format=json&addressdetails=1&zoom=17'
                ),
                json={"error": "Unable to geocode"},
            )
            m.get(**OpenStreetMap51437889_66617012Fixtures().get_requests_mock_kwargs())
            m.get(**OpenStreetMap5143789_661701Fixtures().get_requests_mock_kwargs())
            m.get(**OpenStreetMap00000000_00000000Fixtures().get_requests_mock_kwargs())
            m.get(**OpenStreetMap5251861_1337611Fixtures().get_requests_mock_kwargs())
            m.get(**OpenStreetMap5105254_244456Fixtures().get_requests_mock_kwargs())

            call_command(import_tracks.Command(), "--username", test_username, str(fixture_files_path))
            assert storage_stats.fields_saved == [
                ('for_runners', 'gpxmodel', 'track_svg'),
                ('for_runners', 'gpxmodel', 'gpx_file'),
            ]
            assert storage_stats.fields_read == []

            qs = GpxModel.objects.all()
            existing_tracks = [f'{track.tracked_by} - {track}' for track in qs]
            assert_pformat_equal(
                existing_tracks,
                [
                    'normal_test_user - 2024-07-21 Leffrinckoucke, Nord',
                    'normal_test_user - 2018-02-21 Moers',
                    'normal_test_user - 2011-01-13 Berlin Tiergarten',
                ],
            )

            output = buff.get_output()
            print('-' * 1000)
            print(output)

            self.assertIn("Add new gpx tracks for user: normal_test_user", output)
            self.assertIn("1 - Add new track: 2024-07-21 Leffrinckoucke, Nord", output)
            self.assertIn("2 - Add new track: 2018-02-21 Moers", output)
            self.assertIn("3 - Add new track: 2011-01-13 Berlin Tiergarten", output)
            self.assertIn("Added 3 new gpx tracks.", output)
            self.assertIn("User normal_test_user has now 3 tracks.", output)

            assert qs.count() == 3
            assert storage_stats.fields_read == []
        assert_snapshot(got=weather_mock.call_data)
