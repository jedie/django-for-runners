"""
    Test API connection to metaweather.com via for_runners.weather

    https://www.metaweather.com/api/

    created 21.06.2018 by Jens Diemer <opensource@jensdiemer.de>
    :copyleft: 2018 by the django-for-runners team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import logging

import requests_mock
from bx_py_utils.test_utils.datetime import parse_dt
from django.test import SimpleTestCase

from for_runners.tests.fixtures.weather import Weather5141_678_20180621Fixtures, WeatherWrongLatitudeFixtures
from for_runners.tests.utils import AssertsMixin, ClearCacheMixin
from for_runners.weather import NoWeatherData, weather


class WeatherTest(ClearCacheMixin, AssertsMixin, SimpleTestCase):
    def test_happy_path(self):
        with self.assertLogs('for_runners', level=logging.INFO), requests_mock.mock() as m:
            m.get(**Weather5141_678_20180621Fixtures().get_requests_mock_kwargs())
            temperature, weather_state = weather.coordinates2weather(
                # Duisburg - https://www.google.de/maps/@51.4109,6.7828,12z
                latitude=51.4109,
                longitude=6.7828,
                dt=parse_dt('2018-06-21T14:30:24+01:00'),
            )

        self.assert_equal_rounded(temperature, 16.4, decimal_places=2)
        self.assertEqual(weather_state, 'Overcast')

    def test_error(self):
        with (
            self.assertLogs('for_runners', level=logging.INFO),
            requests_mock.mock() as m,
            self.assertRaisesMessage(
                NoWeatherData,
                'Latitude must be in range of -90 to 90°. Given: 91.0.',
            ),
        ):
            m.get(**WeatherWrongLatitudeFixtures().get_requests_mock_kwargs())
            weather.coordinates2weather(
                latitude=91,  # Latitude must be in range of -90 to 90°
                longitude=0,
                dt=parse_dt('2024-07-01T18:10:02+01:00'),
            )
