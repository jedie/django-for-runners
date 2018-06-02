import unittest
from pathlib import Path

# https://github.com/jedie/django-for-runners
from for_runners.gpx import parse_gpx_file

BASE_PATH = Path(__file__).parent


class GpxTests(unittest.TestCase):

    def test_parse_gpx(self):
        filepath = Path(BASE_PATH, "fixture_files/garmin_connect_1.gpx")

        gpxpy_instance = parse_gpx_file(filepath)

        first_point = gpxpy_instance.tracks[0].segments[0].points[0]
        self.assertEqual(first_point.latitude, 51.43788929097354412078857421875)
        self.assertEqual(first_point.longitude, 6.617012657225131988525390625)

        extensions = first_point.extensions
        self.assertEqual(1, len(extensions))
        self.assertEqual(extensions[0].getchildren()[0].text.strip(), "125")  # hr
        self.assertEqual(extensions[0].getchildren()[1].text.strip(), "75")  # cad
