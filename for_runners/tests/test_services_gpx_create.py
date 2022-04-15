"""
    created 12.06.2018 by Jens Diemer <opensource@jensdiemer.de>
    :copyleft: 2018 by the django-for-runners team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


import requests_mock
from django.test import TestCase
from django_tools.unittest_utils.assertments import assert_pformat_equal
from django_tools.unittest_utils.user import TestUserMixin
from override_storage import locmem_stats_override_storage

from for_runners.services.gpx_create import add_from_file, add_from_files, add_gpx
from for_runners.tests.fixture_files import FIXTURES_PATH, fixture_content
from for_runners.tests.fixtures.metaweather import (
    MetaWeather4695_744Fixtures,
    MetaWeather5144_662Fixtures,
    MetaWeather5252_1338Fixtures,
    MetaWeather648820_2018_2_21Fixtures,
)
from for_runners.tests.utils import ClearCacheMixin


class GpxTests(TestUserMixin, ClearCacheMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.user = self._get_user(usertype="normal")

    def assert_garmin_connect_1_gpx(self, instance):
        print(instance)

        self.assertEqual(repr(instance), "<GpxModel: 2018-02-21>")

        self.assertEqual(instance.points_no, 3)
        self.assertEqual(round(instance.length, 3), 4.727)
        self.assertEqual(instance.duration_s, 2)
        self.assertEqual(round(instance.pace, 3), 7.052)
        self.assertEqual(instance.heart_rate_avg, 125)

        self.assertEqual(instance.get_short_slug(), "2018-02-21")

    def test_add_gpx(self):
        with locmem_stats_override_storage() as storage_stats, requests_mock.mock() as m:
            m.get(**MetaWeather5144_662Fixtures().get_requests_mock_kwargs())
            m.get(**MetaWeather648820_2018_2_21Fixtures().get_requests_mock_kwargs())
            gpx_content = fixture_content('garmin_connect_1.gpx', mode='r')
            instance = add_gpx(gpx_content=gpx_content, user=self.user)
            self.assert_garmin_connect_1_gpx(instance)
        assert storage_stats.fields_saved == [
            ('for_runners', 'gpxmodel', 'track_svg'),
            ('for_runners', 'gpxmodel', 'gpx_file'),
        ]
        assert storage_stats.fields_read == []

    def test_add_from_file(self):
        with locmem_stats_override_storage() as storage_stats, requests_mock.mock() as m:
            m.get(**MetaWeather5144_662Fixtures().get_requests_mock_kwargs())
            m.get(**MetaWeather648820_2018_2_21Fixtures().get_requests_mock_kwargs())
            instance = add_from_file(
                gpx_file_file_path=FIXTURES_PATH / 'garmin_connect_1.gpx', user=self.user
            )
            self.assert_garmin_connect_1_gpx(instance)
        assert storage_stats.fields_saved == [
            ('for_runners', 'gpxmodel', 'track_svg'),
            ('for_runners', 'gpxmodel', 'gpx_file'),
        ]
        assert storage_stats.fields_read == []

    def test_add_from_files(self):
        with locmem_stats_override_storage() as storage_stats, requests_mock.mock() as m:
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
            instances = [
                str(instance)
                for instance in add_from_files(
                    gpx_files_file_path=FIXTURES_PATH,
                    user=self.user,
                    skip_errors=True,
                )
            ]
            assert_pformat_equal(instances, ["2018-02-21", "2011-01-13"])
        assert storage_stats.fields_saved == [
            ('for_runners', 'gpxmodel', 'track_svg'),
            ('for_runners', 'gpxmodel', 'gpx_file'),
        ]
        assert storage_stats.fields_read == []
