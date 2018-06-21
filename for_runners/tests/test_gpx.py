"""
    created 2018 by Jens Diemer <opensource@jensdiemer.de>
    :copyleft: 2018 by the django-for-runners team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import math
import operator
import unittest
from datetime import datetime
from functools import reduce
from pathlib import Path
# https://github.com/jedie/django-for-runners
from pprint import pprint

from for_runners.tests.base import BaseTestCase
from for_runners.tests.utils import generate_gpx_track, lon2kilometers, kilometers2lon_count, earth_circumference
from for_runners.gpx import GpxMedian, iter_distances, parse_gpx_file
from gpxpy.gpx import GPX, GPXTrack, GPXTrackPoint, GPXTrackSegment

BASE_PATH = Path(__file__).parent


class GpxTests(BaseTestCase):

    def test_parse_gpx(self):
        filepath = Path(BASE_PATH, "fixture_files/garmin_connect_1.gpx")

        gpxpy_instance = parse_gpx_file(filepath)

        first_point = gpxpy_instance.tracks[0].segments[0].points[0]
        self.assertEqual(first_point.latitude, 51.43788929097354412078857421875)
        self.assertEqual(first_point.longitude, 6.617012657225131988525390625)

        extensions = first_point.extensions
        self.assertEqual(1, len(extensions))
        self.assertEqual(extensions[0].getchildren()[0].text.strip(), "120")  # hr
        self.assertEqual(extensions[0].getchildren()[1].text.strip(), "70")  # cad

    def test_parse_noi_track_gpx(self):
        filepath = Path(BASE_PATH, "fixture_files/no_track_points.gpx")

        gpxpy_instance = parse_gpx_file(filepath)
        print(gpxpy_instance)
        self.assertEqual(
            repr(gpxpy_instance),
            "GPX(waypoints=[GPXWaypoint(51.43788, 6.61701, name='Somewhere', description='foobar', symbol='Waypoint')])"
        )

    def test_parse_no_heart_rate_gpx(self):
        filepath = Path(BASE_PATH, "fixture_files/garmin_no_heart_rate.gpx")

        gpxpy_instance = parse_gpx_file(filepath)
        print(gpxpy_instance)
        self.assertEqual(
            repr(gpxpy_instance), "GPX(tracks=[GPXTrack(name='Foo Bar', segments=[GPXTrackSegment(points=[...])])])"
        )

    def test_iter_distance(self):

        # containes 3 points:
        filepath = Path(BASE_PATH, "fixture_files/garmin_connect_1.gpx")

        gpxpy_instance = parse_gpx_file(filepath)
        distances = []
        total_points = []
        total_distance = 0
        for section_distance, points in iter_distances(gpxpy_instance, distance=1):
            distances.append(section_distance)
            total_distance += section_distance
            for point in points:
                total_points.append((point.latitude, point.longitude))

        self.assertEqual(
            total_points, [(51.437889290973544, 6.617012657225132), (51.43786800093949, 6.617006119340658),
                           (51.437847297638655, 6.6170057002455)]
        )

        self.assert_equal_rounded(gpxpy_instance.length_3d(), 4.71811430037482)
        self.assert_equal_rounded(total_distance, 4.71811430037482)

        self.assertEqual(distances, [0, 2.408703900785011, 2.3094103597382065])


class GpxMedianTests(BaseTestCase):

    def test_garmin_connect_1_gpx(self):
        # containes 3 points:
        filepath = Path(BASE_PATH, "fixture_files/garmin_connect_1.gpx")
        total_distance = 4.718114260523217

        gpxpy_instance = parse_gpx_file(filepath)

        gpx_median = GpxMedian(gpxpy_instance, distance=1)
        self.assertEqual(gpx_median.total_distance, total_distance)

        distances = tuple(gpx_median.iter_section_distance())
        self.assertEqual(reduce(operator.add, distances), total_distance)
        self.assertEqual(distances, (0, 2.408703900785011, 2.3094103597382065))

    def test_iter_extension_data(self):
        gpx_median = GpxMedian(
            gpxpy_instance = parse_gpx_file(Path(BASE_PATH, "fixture_files/garmin_connect_1.gpx")),
            distance=1
        )

        hr_data = tuple(gpx_median.iter_extension_data(key="hr"))
        pprint(hr_data)
        self.assertEqual(hr_data, (([120], 120, 120, 120), ([125], 125, 125, 125), ([130], 130, 130, 130)))

        cad_data = tuple(gpx_median.iter_extension_data(key="cad"))
        pprint(cad_data)
        self.assertEqual(cad_data, (([70], 70, 70, 70), ([75], 75, 75, 75), ([80], 80, 80, 80)))

    def test_latitude_calculation(self):
        gpxpy_instance = GPX()
        gpxpy_instance.tracks.append(GPXTrack())
        gpxpy_instance.tracks[0].segments.append(GPXTrackSegment())
        points = gpxpy_instance.tracks[0].segments[0].points

        longitude_distance_km = 111.19492664455873

        self.assertEqual(lon2kilometers(lon_count=1), longitude_distance_km)
        self.assertEqual(kilometers2lon_count(longitude_distance_km), 1)

        for lon_count in range(10):
            distance_km = lon2kilometers(lon_count)
            self.assert_equal_rounded(distance_km, longitude_distance_km*lon_count)
            self.assert_equal_rounded(kilometers2lon_count(distance_km), lon_count, decimal_places=0)

    def test_generate_gpx_track(self):

        track_length_km=earth_circumference/2

        gpxpy_instance = generate_gpx_track(track_length_km=track_length_km, point_count=180, pace_min=6, start_longitude=0, start_date=datetime(2018, 5, 30, 10, 00))
        print(gpxpy_instance.to_xml())

        self.assertEqual(gpxpy_instance.get_points_no(), 181) # 180 + No.0

        gpxpy_length_2d_km = gpxpy_instance.length_2d()/1000
        self.assert_equal_rounded(gpxpy_length_2d_km, track_length_km)

        gpxpy_length_3d_km = gpxpy_instance.length_3d()/1000
        self.assert_equal_rounded(gpxpy_length_3d_km, track_length_km)

        # 20015.08679602057
        # 20015.086796020572
