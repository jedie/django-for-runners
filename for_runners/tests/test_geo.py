from unittest import TestCase

# https://github.com/jedie/django-for-runners
from for_runners.geo import reverse_geo


class GeoTests(TestCase):
    def test_reverse_geo(self):

        # first point from: for_runners/tests/fixture_files/garmin_connect_1.gpx
        lat = "51.43788929097354412078857421875"
        lon = "6.617012657225131988525390625"

        address = reverse_geo(lat, lon)
        assert address.short == 'Moers'
        assert address.full.endswith('Moers, Kreis Wesel, Nordrhein-Westfalen, 47447, Deutschland')
