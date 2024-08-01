"""
    created 12.06.2018 by Jens Diemer <opensource@jensdiemer.de>
    :copyleft: 2018 by the django-for-runners team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import gpxpy
import requests_mock
from bx_py_utils.test_utils.snapshot import assert_snapshot
from django.test import TestCase
from django_tools.unittest_utils.assertments import assert_pformat_equal
from django_tools.unittest_utils.user import TestUserMixin
from override_storage import locmem_stats_override_storage

from for_runners.services.gpx_create import add_from_file, add_from_files, add_gpx
from for_runners.tests.fixture_files import FIXTURES_PATH, fixture_content
from for_runners.tests.fixtures.openstreetmap import (
    OpenStreetMap00000000_00000000Fixtures,
    OpenStreetMap0_0Fixtures,
    OpenStreetMap5105254_244456Fixtures,
    OpenStreetMap5143785_661701Fixtures,
    OpenStreetMap5143789_661701Fixtures,
    OpenStreetMap5251861_1337611Fixtures,
)
from for_runners.tests.mocks.weather_mock import WeatherMock
from for_runners.tests.utils import ClearCacheMixin


class GpxTests(TestUserMixin, ClearCacheMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.user = self._get_user(usertype="normal")

    def assert_garmin_connect_1_gpx(self, instance):
        self.assertEqual(repr(instance), "<GpxModel: 2018-02-21 Moers>")

        self.assertEqual(instance.points_no, 3)
        self.assertEqual(round(instance.length, 3), 4.727)
        self.assertEqual(instance.duration_s, 2)
        self.assertEqual(round(instance.pace, 3), 7.052)
        self.assertEqual(instance.heart_rate_avg, 125)

        self.assertEqual(instance.get_short_slug(), "2018-02-21-moers")
        self.assertEqual(instance.get_short_slug(prefix_id=True), '20180221_1430_umd2rr-moers')

    def test_add_gpx(self):
        with (
            locmem_stats_override_storage() as storage_stats,
            requests_mock.mock() as m,
            WeatherMock() as weather_mock,
        ):
            m.get(**OpenStreetMap5143785_661701Fixtures().get_requests_mock_kwargs())
            m.get(**OpenStreetMap5143789_661701Fixtures().get_requests_mock_kwargs())
            gpx_content = fixture_content('garmin_connect_1.gpx', mode='r')
            gpx = gpxpy.parse(gpx_content)
            instance = add_gpx(gpx=gpx, user=self.user)
            self.assert_garmin_connect_1_gpx(instance)
        assert storage_stats.fields_saved == [
            ('for_runners', 'gpxmodel', 'track_svg'),
            ('for_runners', 'gpxmodel', 'gpx_file'),
        ]
        assert storage_stats.fields_read == []

        self.assertEqual(
            weather_mock.call_data,
            [
                {
                    'latitude': 51.437889290973544,
                    'longitude': 6.617012657225132,
                    'dt': '2018-02-21T14:30:50+00:00',
                },
                {
                    'latitude': 51.437847297638655,
                    'longitude': 6.6170057002455,
                    'dt': '2018-02-21T14:30:52+00:00',
                },
            ],
        )

    def test_add_from_file(self):
        with (
            locmem_stats_override_storage() as storage_stats,
            requests_mock.mock() as m,
            WeatherMock() as weather_mock,
        ):
            m.get(**OpenStreetMap5143785_661701Fixtures().get_requests_mock_kwargs())
            m.get(**OpenStreetMap5143789_661701Fixtures().get_requests_mock_kwargs())
            instance = add_from_file(track_path=FIXTURES_PATH / 'garmin_connect_1.gpx', user=self.user)
            self.assert_garmin_connect_1_gpx(instance)
        assert storage_stats.fields_saved == [
            ('for_runners', 'gpxmodel', 'track_svg'),
            ('for_runners', 'gpxmodel', 'gpx_file'),
        ]
        assert storage_stats.fields_read == []
        self.assertEqual(
            weather_mock.call_data,
            [
                {
                    'latitude': 51.437889290973544,
                    'longitude': 6.617012657225132,
                    'dt': '2018-02-21T14:30:50+00:00',
                },
                {
                    'latitude': 51.437847297638655,
                    'longitude': 6.6170057002455,
                    'dt': '2018-02-21T14:30:52+00:00',
                },
            ],
        )

    def test_add_from_files(self):
        print('+' * 1000)
        with (
            locmem_stats_override_storage() as storage_stats,
            requests_mock.mock() as m,
            WeatherMock() as weather_mock,
        ):
            m.get(**OpenStreetMap5143785_661701Fixtures().get_requests_mock_kwargs())
            m.get(**OpenStreetMap5143789_661701Fixtures().get_requests_mock_kwargs())
            m.get(**OpenStreetMap0_0Fixtures().get_requests_mock_kwargs())
            m.get(**OpenStreetMap00000000_00000000Fixtures().get_requests_mock_kwargs())
            m.get(**OpenStreetMap5251861_1337611Fixtures().get_requests_mock_kwargs())
            m.get(**OpenStreetMap5105254_244456Fixtures().get_requests_mock_kwargs())
            existing_tracks = [
                str(instance)
                for instance in add_from_files(
                    tracks_path=FIXTURES_PATH,
                    user=self.user,
                    skip_errors=True,
                )
            ]
            assert_pformat_equal(
                existing_tracks,
                [
                    '2024-07-21 Leffrinckoucke, Nord',
                    '2018-02-21 Moers',
                    '2011-01-13 Berlin Tiergarten',
                ],
            )

        assert storage_stats.fields_saved == [
            ('for_runners', 'gpxmodel', 'track_svg'),
            ('for_runners', 'gpxmodel', 'gpx_file'),
        ]
        assert storage_stats.fields_read == []
        assert_snapshot(got=weather_mock.call_data)
