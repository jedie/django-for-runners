from unittest import TestCase

import requests_mock
from django.conf import settings
from django.core.cache import cache

from for_runners.geo import reverse_geo
from for_runners.tests.fixtures.openstreetmap import OpenStreetMap5143789_661701Fixtures
from for_runners.tests.utils import ClearCacheMixin


class GeoTests(ClearCacheMixin, TestCase):
    def test_reverse_geo(self):

        # first point from: for_runners/tests/fixture_files/garmin_connect_1.gpx
        lat = 51.43788929097354412078857421875
        lon = 6.617012657225131988525390625

        with requests_mock.mock() as m:
            m.get(**OpenStreetMap5143789_661701Fixtures().get_requests_mock_kwargs())

            address = reverse_geo(lat, lon)

        assert address.short == 'Moers'
        assert address.full == (
            'Zur Alten Wassermühle, Vinn, Moers, Kreis Wesel,'
            ' Nordrhein-Westfalen, 47447, Deutschland'
        )

        # Check if cache works in tests:
        self.assertEqual(settings.CACHES['default']['BACKEND'], 'django.core.cache.backends.locmem.LocMemCache')
        cache.set('foo', 'bar', timeout=None)
        assert cache.get('foo') == 'bar'

        # Cache filled?
        address = cache.get('reverse_geo_51.43789_6.61701')
        assert address
        assert address == (
            'Zur Alten Wassermühle, Vinn, Moers, Kreis Wesel,'
            ' Nordrhein-Westfalen, 47447, Deutschland',
            {
                'ISO3166-2-lvl4': 'DE-NW',
                'city': 'Moers',
                'country': 'Deutschland',
                'country_code': 'de',
                'county': 'Kreis Wesel',
                'hamlet': 'Vinn',
                'postcode': '47447',
                'road': 'Zur Alten Wassermühle',
                'state': 'Nordrhein-Westfalen',
            },
        )

        # Second request is cached -> no request
        with requests_mock.mock():
            address = reverse_geo(lat, lon)

        assert address.short == 'Moers'
        assert address.full == (
            'Zur Alten Wassermühle, Vinn, Moers, Kreis Wesel,'
            ' Nordrhein-Westfalen, 47447, Deutschland'
        )
