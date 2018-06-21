"""
    created 19.06.2018 by Jens Diemer <opensource@jensdiemer.de>
    :copyleft: 2018 by the django-for-runners team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""
import math
from datetime import datetime, timedelta

from gpxpy.gpx import GPX, GPXTrack, GPXTrackSegment, GPXTrackPoint


# FIXME: gpxpy used 40030.174 km but WGS 84 is 40075.017 km
# see: https://github.com/tkrajina/gpxpy/issues/123

# circumference of the equator is 40075.017 km (WGS 84)
# earth_circumference = 2*math.pi*6378.137 # ==> 40075.016685578485
# km_per_longitude = earth_circumference / 360  # ==> 111.31949166666666 km


# # gpxpy used 40030.174 km
earth_circumference = 2*math.pi*6371.0 # ==> 40030.173592041145
km_per_longitude = earth_circumference / 360  # ==> 111.19492664455873 km


def lon2kilometers(lon_count):
    """
    return the distance in kilometers between the given longitude count.
    (Only valid at the equator: longitude=0 and elevation=0)

    >>> round(lon2kilometers(lon_count=1),2)  # 111.19492664455873
    111.19
    >>> round(lon2kilometers(lon_count=10),2) # 1111.9492664455872
    1111.95
    """
    return lon_count * km_per_longitude


def kilometers2lon_count(kilometers):
    """
    return the longitude count for the given kilometer distances.
    (Only valid at the equator: longitude=0 and elevation=0)

    >>> round(kilometers2lon_count(111.19492664455873),1)
    1.0
    >>> round(kilometers2lon_count(1111.9492664455872),1)
    10.0
    """
    return kilometers / km_per_longitude


def generate_gpx_track(track_length_km, point_count, pace_min, start_longitude=0, start_date=datetime(2018, 5, 30, 10, 00)):
    distance_km = track_length_km / point_count
    print("km between points:", distance_km)

    longitude_diff = kilometers2lon_count(distance_km)
    print("longitude diff:", longitude_diff)

    time_delta = timedelta(minutes=(pace_min*distance_km))
    print("time delta:", time_delta)

    gpxpy_instance = GPX()
    gpxpy_instance.tracks.append(GPXTrack())
    gpxpy_instance.tracks[0].segments.append(GPXTrackSegment())
    points = gpxpy_instance.tracks[0].segments[0].points
    points.append(GPXTrackPoint(latitude=0, longitude=start_longitude, elevation=0, time=start_date))
    print("Start point:", points[-1])

    td = 0
    current_longitude = start_longitude
    current_datetime = start_date
    for point_no in range(point_count):
        current_longitude += longitude_diff
        current_datetime += time_delta
        points.append(GPXTrackPoint(latitude=0, longitude=current_longitude, elevation=0, time=current_datetime))
        print("point %i: %s" % (point_no+1, points[-1]))

        print("\ttime diff:", points[-1].time_difference(points[-2]))
        print("\tdistance 2d:", points[-1].distance_2d(points[-2]))
        print("\tdistance 3d:", points[-1].distance_3d(points[-2]))
        td += points[-1].distance_3d(points[-2])
        print("\t", td)

    return gpxpy_instance
