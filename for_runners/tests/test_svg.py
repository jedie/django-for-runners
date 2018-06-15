"""
    created 15.06.2018 by Jens Diemer <opensource@jensdiemer.de>
    :copyleft: 2018 by the django-for-runners team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import unittest
from pathlib import Path

from for_runners.gpx import parse_gpx_file
from for_runners.svg import gpx2svg_string

BASE_PATH = Path(__file__).parent


class SvgTest(unittest.TestCase):

    def test_svg(self):
        filepath = Path(BASE_PATH, "fixture_files/parliament_buildings.gpx")

        gpxpy_instance = parse_gpx_file(filepath)
        svg_string = gpx2svg_string(gpxpy_instance, pretty=True)
        print("-" * 79)
        print(svg_string)
        print("-" * 79)

        svg_reference = Path(BASE_PATH, "fixture_files/parliament_buildings.svg")
        with svg_reference.open("r") as f:
            svg_reference_string = f.read()

        self.assertEqual(svg_string, svg_reference_string)
