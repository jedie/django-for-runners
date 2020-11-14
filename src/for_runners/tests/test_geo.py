from unittest import TestCase

import requests_mock

from for_runners.geo import reverse_geo


class GeoTests(TestCase):
    def test_reverse_geo(self):

        # first point from: for_runners/tests/fixture_files/garmin_connect_1.gpx
        lat = "51.43788929097354412078857421875"
        lon = "6.617012657225131988525390625"

        osm_json_response = {
            'place_id': 273953846,
            'licence': 'Data © OpenStreetMap contributors, ODbL 1.0. https://osm.org/copyright',
            'osm_type': 'way',
            'osm_id': 764409683,
            'lat': '51.438802550000005',
            'lon': '6.616602053045958',
            'display_name': (
                        '148, Filder Straße, Vinn,'
                        ' Moers, Kreis Wesel,'
                        ' North Rhine-Westphalia,'
                        ' 47447, Germany'
            ),
            'address': {
                'house_number': '148',
                'road': 'Filder Straße',
                        'hamlet': 'Vinn',
                        'suburb': 'Moers',
                        'city': 'Moers',
                        'county': 'Kreis Wesel',
                        'state': 'North Rhine-Westphalia',
                        'postcode': '47447',
                        'country': 'Germany',
                        'country_code': 'de'},
            'boundingbox': [
                '51.4387285',
                '51.4388694',
                '6.6162302',
                '6.6169724']}

        with requests_mock.mock() as m:
            m.get(
                ('https://nominatim.openstreetmap.org/reverse'
                 '?lat=51.437889290973544'
                 '&lon=6.617012657225132'
                 '&format=json'
                 '&addressdetails=1'),
                headers={'content-type': 'application/json'},
                json=osm_json_response
            )
            address = reverse_geo(lat, lon)

        assert address.short == 'Moers'
        assert address.full == (
            '148, Filder Straße, Vinn, Moers, Kreis Wesel, North Rhine-Westphalia, 47447, Germany'
        )
