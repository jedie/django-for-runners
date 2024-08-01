from datetime import datetime, timedelta, timezone

from bx_py_utils.test_utils.datetime import parse_dt
from django.test import SimpleTestCase
from gpxpy.gpx import GPX

from for_runners.gpx_tools.kml import Coordinates, kml2gpx, parse_coordinates, parse_datetime
from for_runners.tests.fixture_files import get_fixture_path


class KmlTestCase(SimpleTestCase):

    def test_parse_coordinates(self):
        self.assertEqual(
            parse_coordinates('2.444563,51.052540,8.0'),
            Coordinates(longitude=2.444563, latitude=51.05254, altitude=8.0),
        )
        self.assertEqual(
            parse_coordinates('-2.444563,-51.052540,-8.0'),
            Coordinates(longitude=-2.444563, latitude=-51.05254, altitude=-8.0),
        )
        self.assertEqual(
            parse_coordinates('  2.444563 , 51.052540 , 8.0  '),
            Coordinates(longitude=2.444563, latitude=51.05254, altitude=8.0),
        )
        self.assertIsNone(parse_coordinates('2.444563,51.052540'))
        self.assertIsNone(parse_coordinates('abc,def,ghi'))

    def test_parse_datetime(self):
        self.assertEqual(
            parse_datetime('2024/07/21 14:30:24 UTC+01:00'),
            datetime(
                2024,
                7,
                21,
                14,
                30,
                24,
                tzinfo=timezone(timedelta(hours=1)),
            ),
        )
        self.assertEqual(
            parse_datetime('2024/07/21 14:30:24 UTC-05:30'),
            datetime(
                2024,
                7,
                21,
                14,
                30,
                24,
                tzinfo=timezone(timedelta(hours=-5, minutes=-30)),
            ),
        )

        with self.assertLogs('for_runners.gpx_tools.kml', 'WARNING') as cm:
            self.assertIsNone(parse_datetime('2024/07/21 14:30:24'))
            self.assertIn('Failed to parse datetime string', '\n'.join(cm.output))

        with self.assertLogs('for_runners.gpx_tools.kml', 'WARNING') as cm:
            self.assertIsNone(parse_datetime('21/07/2024 14:30:24 UTC+01:00'))
            self.assertIn('Failed to parse datetime string', '\n'.join(cm.output))

        with self.assertLogs('for_runners.gpx_tools.kml', 'WARNING') as cm:
            self.assertIsNone(parse_datetime('2024/07/21 14:30:24 UTC+1:00'))
            self.assertIn('Failed to parse timezone offset', '\n'.join(cm.output))

    def test_kml2gpx(self):
        fixture_path = get_fixture_path('PentaxK1.KML')

        with self.assertLogs('for_runners.gpx_tools.kml', 'WARNING'):
            gpx = kml2gpx(fixture_path)
        self.assertIsInstance(gpx, GPX)

        first_point = gpx.tracks[0].segments[0].points[0]
        self.assertEqual(first_point.latitude, 51.052540)
        self.assertEqual(first_point.longitude, 2.444563)
        self.assertEqual(first_point.elevation, 8.0)
        self.assertEqual(first_point.time, parse_dt('2024-07-21T14:30:24+01:00'))

        last_point = gpx.tracks[0].segments[0].points[-1]
        self.assertEqual(last_point.latitude, 50.944859)
        self.assertEqual(last_point.longitude, 1.847900)
        self.assertEqual(last_point.elevation, 14.0)
        self.assertEqual(last_point.time, parse_dt('2024-07-21T21:28:31+01:00'))
