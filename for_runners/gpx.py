"""
    created 31.05.2018 by Jens Diemer <opensource@jensdiemer.de>
    :copyleft: 2018 by the django-for-runners team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""
import collections
import io
import statistics
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


def get_2d_coordinate_list(gpxpy_instance):
    lat_list = []
    lon_list = []
    for latitude, longitude, elevation in iter_coordinates(gpxpy_instance):
        lat_list.append(latitude)
        lon_list.append(longitude)

    if not lat_list or not lon_list:
        raise GpxDataError("No track points in file!")

    return (lat_list, lon_list)


def add_extension_data(point):
    """
    Add all existing extension_data dict to the point.
    Garmin can contain:
        'hr' -> heart rate
        'cad' -> cadence value
    """
    extension_data = {}
    extensions = point.extensions
    if extensions:
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
            extension_data[tag] = value

    point.extension_data = extension_data
    return point


def iter_extensions(points):
    for point in points:
        point = add_extension_data(point)  # set: point.extension_data dict
        yield point


def get_extension_data(gpxpy_instance):
    """
    return a dict with all extension values from all track points.
    """
    extension_data = collections.defaultdict(list)
    for point in iter_points(gpxpy_instance):
        point = add_extension_data(point)  # set: point.extension_data dict
        for key, value in point.extension_data.items():
            extension_data[key].append(value)

    return dict(extension_data)


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


def iter_distances(gpxpy_instance, distance):
    """
    iterate over GPXTrackPoint() instances at intervals of <distance> in meters
    """
    iterator = iter_points(gpxpy_instance)

    previous_point = next(iterator)
    points = [previous_point]
    old_latitude, old_longitude, old_elevation = previous_point.latitude, previous_point.longitude, previous_point.elevation

    count = 1
    next_distance = distance
    section_distance = 0
    for point in iterator:
        point = add_extension_data(point)  # set: point.extension_data dict
        points.append(point)
        latitude, longitude, elevation = point.latitude, point.longitude, point.elevation

        point_distance = geo_distance(old_latitude, old_longitude, old_elevation, latitude, longitude, elevation)

        previous_section_distance = section_distance
        section_distance += point_distance

        old_latitude, old_longitude, old_elevation = latitude, longitude, elevation

        if section_distance >= next_distance:

            # Calculate the deviation from the ideal distance:
            current_difference = section_distance - next_distance
            previous_difference = abs(previous_section_distance - next_distance)

            print(
                "no. %03i: previous point %.1fm diff: %.1fm vs. current point %.1fm diff: %.1fm" %
                (count, previous_section_distance, previous_difference, section_distance, current_difference)
            )

            # We didn't use the >count< for resulting kilometers:
            # Maybe the point density is very low and the real distance is greater than kilometers ;)
            # Use convert_distance_in_km() and the real distance.

            if previous_difference < current_difference:
                # The deviation from the previous position is smaller:
                yield previous_section_distance, points[:-1]
                points = [point]
                section_distance = point_distance
            else:
                yield section_distance, points
                points = []
                section_distance = 0

            count += 1
            next_distance = distance * count

    # the last points
    yield section_distance, points


class GpxSection:

    def __init__(self, distance, points):
        self.distance = distance
        self.points = points

        self.extension_data = collections.defaultdict(list)
        for point in points:
            point = add_extension_data(point)  # set: point.extension_data dict
            for key, value in point.extension_data.items():
                self.extension_data[key].append(value)

        self.extension_data_median = {}

        for key in self.extension_data.keys():
            values = self.extension_data[key]
            print(key, values)

            self.extension_data_median["%s_min" % key] = min(values)
            self.extension_data_median["%s_max" % key] = max(values)
            self.extension_data_median["%s_avg" % key] = statistics.median(values)

    def get_extension_min(self, key):
        return self.extension_data_median["%s_min" % key]

    def get_extension_max(self, key):
        return self.extension_data_median["%s_max" % key]

    def get_extension_avg(self, key):
        return self.extension_data_median["%s_avg" % key]


class GpxMedian:

    def __init__(self, gpxpy_instance, distance):
        self.total_distance = 0
        self.sections = []
        for section_distance, points in iter_distances(gpxpy_instance, distance=distance):
            self.total_distance += section_distance
            self.sections.append(GpxSection(section_distance, points))

    def iter_section_distance(self):
        for section in self.sections:
            yield section.distance

    def iter_extension_data(self, key):
        for section in self.sections:
            min_value = section.get_extension_min(key)
            max_value = section.get_extension_max(key)
            avg_value = section.get_extension_avg(key)
            yield section.extension_data[key], min_value, max_value, avg_value


