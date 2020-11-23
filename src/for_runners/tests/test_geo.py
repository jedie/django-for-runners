from pathlib import Path
from unittest import TestCase

import requests_mock

from for_runners.geo import reverse_geo


BASE_PATH = Path(__file__).parent


class GeoTests(TestCase):
    def test_reverse_geo(self):

        # first point from: for_runners/tests/fixture_files/garmin_connect_1.gpx
        lat = "51.43788929097354412078857421875"
        lon = "6.617012657225131988525390625"

        with requests_mock.mock() as m:
            m.get(
                ('https://nominatim.openstreetmap.org/reverse'
                 '?lat=51.437889290973544&lon=6.617012657225132'
                 '&format=json&addressdetails=1'),
                headers={'Content-Type': 'application/json'},
                content=open(BASE_PATH / 'fixture_files/osm_reverse1.json', 'rb').read()
            )
            address = reverse_geo(lat, lon)
        assert address.short == 'Moers'
        assert address.full == (
            '148, Filder Straße, Vinn, Moers, Kreis Wesel, Nordrhein-Westfalen, 47447, Deutschland'
        )
