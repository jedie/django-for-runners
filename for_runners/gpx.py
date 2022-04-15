"""
    created 31.05.2018 by Jens Diemer <opensource@jensdiemer.de>
    :copyleft: 2018 by the django-for-runners team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""
import base64
import collections
import hashlib
import statistics

import gpxpy
from gpxpy.geo import distance as geo_distance

# https://github.com/jedie/django-for-runners
from for_runners.exceptions import GpxDataError


Identifier = collections.namedtuple(
    "Identifier", ("start_time, start_lat, start_lon, finish_time, finish_lat, finish_lon")
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
        time_bounds.start_time,
        first_point.latitude,
        first_point.longitude,
        time_bounds.end_time,
        last_point.latitude,
        last_point.longitude,
    )


def cutted_hash(text, hash_name="sha512", length=6):
    h = hashlib.new(hash_name)
    h.update(bytes(text, encoding="UTF-8"))
    digest = h.digest()
    base32_bytes = base64.b32encode(digest)
    hash = base32_bytes.decode("UTF-8")[:length]
    return hash


class GpxIdentifier:
    def __init__(self, gpxpy_instance):
        self.identifier = get_identifier(gpxpy_instance)

    def _identifier_string(self):
        data = []
        data.append(self.identifier.start_time.strftime("%Y%m%d%H%M%S"))
        data.append(f"{self.identifier.start_lat:.25f}")
        data.append(f"{self.identifier.start_lon:.25f}")
        data.append(self.identifier.finish_time.strftime("%Y%m%d%H%M%S"))
        data.append(f"{self.identifier.finish_lat:.25f}")
        data.append(f"{self.identifier.finish_lon:.25f}")
        return "_".join(data)

    def _prefix(self):
        return self.identifier.start_time.strftime("%Y%m%d_%H%M")

    def get_prefix_id(self):
        identifier_string = self._identifier_string()
        result = f"{self._prefix()}_{cutted_hash(identifier_string, length=6)}"
        return result


def parse_gpx(content):
    # if 'creator="Garmin Connect"' in content:
    #     # work-a-round until https://github.com/tkrajina/gpxpy/issues/115#issuecomment-392798245 fixed
    #     return garmin2gpxpy(content)

    return gpxpy.parse(content)


def parse_gpx_file(filepath):
    assert filepath.is_file(), f"File not found: '{filepath}'"
    with filepath.open("r") as f:
        content = f.read()

    return parse_gpx(content)


def iter_points(gpxpy_instance):
    for track in gpxpy_instance.tracks:
        for segment in track.segments:
            yield from segment.points


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
    old_latitude, old_longitude, old_elevation = (
        previous_point.latitude,
        previous_point.longitude,
        previous_point.elevation,
    )

    count = 1
    next_distance = distance
    total_distance = 0
    for point in iterator:
        latitude, longitude, elevation = point.latitude, point.longitude, point.elevation

        previous_total_distance = total_distance
        total_distance += geo_distance(
            old_latitude, old_longitude, old_elevation, latitude, longitude, elevation)

        old_latitude, old_longitude, old_elevation = latitude, longitude, elevation

        if total_distance >= next_distance:

            # Calculate the deviation from the ideal distance:
            current_difference = total_distance - next_distance
            previous_difference = abs(previous_total_distance - next_distance)

            print(
                f"no. {count:03d}: previous point {previous_total_distance:.1f}m"
                f" diff: {previous_difference:.1f}m vs. current point {total_distance:.1f}m"
                f" diff: {current_difference:.1f}m"
            )

            # We didn't use the >count< for resulting kilometers:
            # Maybe the point density is very low and the real distance is greater than kilometers.
            # Use convert_distance_in_km() and the real distance.

            if previous_difference < current_difference:
                # The deviation from the previous position is smaller:
                yield previous_point, previous_total_distance, convert_distance_in_km(
                    previous_total_distance
                )
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
    old_latitude, old_longitude, old_elevation = (
        previous_point.latitude,
        previous_point.longitude,
        previous_point.elevation,
    )

    count = 1
    next_distance = distance
    section_distance = 0
    for point in iterator:
        point = add_extension_data(point)  # set: point.extension_data dict
        points.append(point)
        latitude, longitude, elevation = point.latitude, point.longitude, point.elevation

        point_distance = geo_distance(
            old_latitude, old_longitude, old_elevation, latitude, longitude, elevation
        )

        previous_section_distance = section_distance
        section_distance += point_distance

        old_latitude, old_longitude, old_elevation = latitude, longitude, elevation

        if section_distance >= next_distance:

            # Calculate the deviation from the ideal distance:
            current_difference = section_distance - next_distance
            previous_difference = abs(previous_section_distance - next_distance)

            print(
                f"no. {count:03d}: previous point {previous_section_distance:.1f}m"
                f" diff: {previous_difference:.1f}m vs. current point {section_distance:.1f}m"
                f" diff: {current_difference:.1f}m"
            )

            # We didn't use the >count< for resulting kilometers:
            # Maybe the point density is very low and the real distance is greater than kilometers.
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

            self.extension_data_median[f"{key}_min"] = min(values)
            self.extension_data_median[f"{key}_max"] = max(values)
            self.extension_data_median[f"{key}_avg"] = statistics.median(values)

    def get_extension_min(self, key):
        return self.extension_data_median[f"{key}_min"]

    def get_extension_max(self, key):
        return self.extension_data_median[f"{key}_max"]

    def get_extension_avg(self, key):
        return self.extension_data_median[f"{key}_avg"]


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
