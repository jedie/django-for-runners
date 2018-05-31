"""
    created 31.05.2018 by Jens Diemer <opensource@jensdiemer.de>
    :copyleft: 2018 by the django-for-runners team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""
import collections
import io
from pathlib import Path

import gpxpy

# https://github.com/jedie/django-for-runners
from for_runners.gpx_tools.garmin2gpxpy import garmin2gpxpy

Identifier = collections.namedtuple('Identifier', ('start_time, start_lat, start_lon, finish_time, finish_lat, finish_lon'))


def get_identifier(gpxpy_instance):
    """
    :return: Identifier named tuple
    """
    time_bounds = gpxpy_instance.get_time_bounds()

    first_track = gpxpy_instance.tracks[0]
    first_segment = first_track.segments[0]
    first_point = first_segment.points[0]

    last_track = gpxpy_instance.tracks[-1]
    last_segment = last_track.segments[-1]
    last_point = last_segment.points[-1]

    return Identifier(
        time_bounds.start_time, first_point.latitude, first_point.longitude, time_bounds.end_time, last_point.latitude,
        last_point.longitude
    )


def parse_gpx(content):
    if 'creator="Garmin Connect"' in content:
        # work-a-round until https://github.com/tkrajina/gpxpy/issues/115#issuecomment-392798245 fixed
        return garmin2gpxpy(content)

    temp = io.BytesIO(content)
    return gpxpy.parse(temp)
