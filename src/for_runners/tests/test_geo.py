from unittest import TestCase

import requests_mock
from django.conf import settings
from django.core.cache import cache

from for_runners.geo import reverse_geo
from for_runners.tests.fixture_files import fixture_content
from for_runners.tests.utils import ClearCacheMixin


class GeoTests(ClearCacheMixin, TestCase):
    def test_reverse_geo(self):

        # first point from: for_runners/tests/fixture_files/garmin_connect_1.gpx
        lat = 51.43788929097354412078857421875
        lon = 6.617012657225131988525390625

        with requests_mock.mock() as m:
            m.get(
                (
                    'https://nominatim.openstreetmap.org/reverse'
                    '?lat=51.43789&lon=6.61701&format=json&addressdetails=1&zoom=17'
                ),
                headers={'Content-Type': 'application/json'},
                content=fixture_content('metaweather_5143789_661701.json')
            )
            address = reverse_geo(lat, lon)

        assert address.short == 'Moers'
        assert address.full == (
            '148, Filder Straße, Vinn, Moers, Kreis Wesel, Nordrhein-Westfalen, 47447, Deutschland'
        )

        # Check if cache works in tests:
        assert settings.CACHES['default']['BACKEND'] == (
            'django.core.cache.backends.locmem.LocMemCache'
        )
        cache.set('foo', 'bar', timeout=None)
        assert cache.get('foo') == 'bar'

        # Cache filled?
        address = cache.get('reverse_geo_51.43789_6.61701')
        assert address is not None
        assert address == (
            '148, Filder Straße, Vinn, Moers, Kreis Wesel, Nordrhein-Westfalen, 47447, Deutschland',
            {'city': 'Moers',
             'country': 'Deutschland',
             'country_code': 'de',
             'county': 'Kreis Wesel',
             'hamlet': 'Vinn',
             'house_number': '148',
             'postcode': '47447',
             'road': 'Filder Straße',
             'state': 'Nordrhein-Westfalen',
             'suburb': 'Moers'}
        )

        # Second request is cached -> no request
        with requests_mock.mock():
            address = reverse_geo(lat, lon)

        assert address.short == 'Moers'
        assert address.full == (
            '148, Filder Straße, Vinn, Moers, Kreis Wesel, Nordrhein-Westfalen, 47447, Deutschland'
        )
