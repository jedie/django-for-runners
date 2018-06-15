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
from gpxpy.geo import distance as geo_distance

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


def iter_points(gpxpy_instance):
    for track in gpxpy_instance.tracks:
        for segment in track.segments:
            for point in segment.points:
                yield point


def iter_coordinates(gpxpy_instance):
    for point in iter_points(gpxpy_instance):
        # log.debug('Point at ({0},{1}) -> {2}'.format(point.latitude, point.longitude, point.elevation))
        yield (point.latitude, point.longitude, point.elevation)


def get_2d_coordinate_list(gpxpy_instance):
    lat_list = []
    lon_list = []
    for latitude, longitude, elevation in iter_coordinates(gpxpy_instance):
        lat_list.append(latitude)
        lon_list.append(longitude)

    if not lat_list or not lon_list:
        raise GpxDataError("No track points in file!")

    return (lat_list, lon_list)


def get_extension_data(gpxpy_instance):
    """
    return a dict with all extension values from all track points.
    """
    extension_data = collections.defaultdict(list)

    for point in iter_points(gpxpy_instance):
        extensions = point.extensions
        if not extensions:
            return None

        for child in extensions[0].getchildren():
            tag = child.tag.rsplit("}", 1)[-1]  # FIXME

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


def iter_distance(gpxpy_instance, distance):
    """
    iterate over GPXTrackPoint() instances at intervals of <distance> in meters
    """
    def convert_distance_in_km(distance):
        """
        Calculate the rounded kilometers as integer from the current distance in meters.
        """
        return int(round(distance / 1000))

    iterator = iter_points(gpxpy_instance)

    previous_point = next(iterator)
    old_latitude, old_longitude, old_elevation = previous_point.latitude, previous_point.longitude, previous_point.elevation

    count = 1
    next_distance = distance
    total_distance = 0
    for point in iterator:
        latitude, longitude, elevation = point.latitude, point.longitude, point.elevation

        previous_total_distance = total_distance
        total_distance += geo_distance(old_latitude, old_longitude, old_elevation, latitude, longitude, elevation)

        old_latitude, old_longitude, old_elevation = latitude, longitude, elevation

        if total_distance >= next_distance:

            # Calculate the deviation from the ideal distance:
            current_difference = total_distance - next_distance
            previous_difference = abs(previous_total_distance - next_distance)

            print(
                "no. %03i: previous point %.1fm diff: %.1fm vs. current point %.1fm diff: %.1fm" %
                (count, previous_total_distance, previous_difference, total_distance, current_difference)
            )

            # We didn't use the >count< for resulting kilometers:
            # Maybe the point density is very low and the real distance is greater than kilometers ;)
            # Use convert_distance_in_km() and the real distance.

            if previous_difference < current_difference:
                # The deviation from the previous position is smaller:
                yield previous_point, previous_total_distance, convert_distance_in_km(previous_total_distance)
            else:
                yield point, total_distance, convert_distance_in_km(total_distance)

            count += 1
            next_distance = distance * count

        previous_point = point
