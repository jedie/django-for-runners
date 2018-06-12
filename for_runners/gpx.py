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
from for_runners.exceptions import GpxDataError
from for_runners.gpx_tools.garmin2gpxpy import garmin2gpxpy

Identifier = collections.namedtuple(
    'Identifier', ('start_time, start_lat, start_lon, finish_time, finish_lat, finish_lon')
)


def get_identifier(gpxpy_instance):
    """
    :return: Identifier named tuple
    """
    time_bounds = gpxpy_instance.get_time_bounds()

    try:
        first_track = gpxpy_instance.tracks[0]
    except IndexError:
        raise GpxDataError("Can't get first track")

    try:
        first_segment = first_track.segments[0]
    except IndexError:
        raise GpxDataError("Can't get first segment")

    try:
        first_point = first_segment.points[0]
    except IndexError:
        raise GpxDataError("Can't get first segment point")

    try:
        last_track = gpxpy_instance.tracks[-1]
    except IndexError:
        raise GpxDataError("Can't get last track")

    try:
        last_segment = last_track.segments[-1]
    except IndexError:
        raise GpxDataError("Can't get last segment")

    try:
        last_point = last_segment.points[-1]
    except IndexError:
        raise GpxDataError("Can't get last segment point")

    return Identifier(
        time_bounds.start_time, first_point.latitude, first_point.longitude, time_bounds.end_time, last_point.latitude,
        last_point.longitude
    )


def parse_gpx(content):
    # if 'creator="Garmin Connect"' in content:
    #     # work-a-round until https://github.com/tkrajina/gpxpy/issues/115#issuecomment-392798245 fixed
    #     return garmin2gpxpy(content)

    return gpxpy.parse(content)


def parse_gpx_file(filepath):
    assert filepath.is_file(), "File not found: '%s'" % filepath
    with filepath.open("r") as f:
        content = f.read()

    return parse_gpx(content)


def get_extension_data(gpxpy_instance):
    """
    return a dict with all extension values from all track points.
    """
    extension_data = collections.defaultdict(list)

    for track in gpxpy_instance.tracks:
        for segment in track.segments:
            for point in segment.points:
                extensions = point.extensions
                if not extensions:
                    return None

                for child in extensions[0].getchildren():
                    tag = child.tag.rsplit("}", 1)[-1] # FIXME

                    value = child.text
                    try:
                        if "." in value:
                            value = float(value)
                        else:
                            value = int(value)
                    except ValueError:
                        pass
                    extension_data[tag].append(value)

    return extension_data
