import dataclasses
import datetime
import logging
import re
from typing import BinaryIO

import gpxpy.gpx
from gpxpy.gpx import GPX, GPXTrackPoint
from lxml import etree
from lxml.etree import Element


log = logging.getLogger(__name__)


def get_single_text(node: Element, xpath: str, namespaces) -> str | None:
    if elements := node.xpath(xpath, namespaces=namespaces):
        assert len(elements) == 1, f'Expected 1 element, got {len(elements)}'
        return elements[0].text


@dataclasses.dataclass
class Coordinates:
    longitude: float
    latitude: float
    altitude: float


def parse_coordinates(coordinates: str) -> Coordinates | None:
    """
    >>> parse_coordinates('2.444563,51.052540,8.0')
    Coordinates(longitude=2.444563, latitude=51.05254, altitude=8.0)
    """
    match = re.match(r'\s*(-?\d+\.\d+)\s*,\s*(-?\d+\.\d+)\s*,\s*(-?\d+\.\d+)\s*', coordinates)
    if match:
        lon, lat, alt = map(float, match.groups())
        return Coordinates(longitude=lon, latitude=lat, altitude=alt)


def get_coordinates(placemark: Element, namespaces) -> Coordinates | None:
    if coordinates := get_single_text(placemark, './/kml:coordinates', namespaces=namespaces):
        return parse_coordinates(coordinates)


def parse_datetime(datetime_str) -> datetime.datetime | None:
    dt_part, tz_part = datetime_str.rsplit(' ', 1)

    try:
        dt = datetime.datetime.strptime(dt_part, '%Y/%m/%d %H:%M:%S')
    except ValueError:
        log.exception('Failed to parse datetime string %r', datetime_str)
        return None

    if not tz_part.startswith('UTC'):
        log.warning('Timezone not in UTC format: %r', tz_part)
        return None

    sign = 1 if tz_part[3] == '+' else -1
    try:
        hours_offset = int(tz_part[4:6])
        minutes_offset = int(tz_part[7:9])
    except ValueError:
        log.exception('Failed to parse timezone offset %r', tz_part)
        return None

    tz_offset = datetime.timedelta(hours=sign * hours_offset, minutes=sign * minutes_offset)
    dt = dt.replace(tzinfo=datetime.timezone(tz_offset))
    return dt


def datetime_from_description(placemark: Element, namespaces):
    if description := get_single_text(placemark, 'kml:description', namespaces=namespaces):
        dt_str = description.partition('<br>')[0]
        return parse_datetime(dt_str)


def kml2gpx(kml_file: BinaryIO) -> GPX:
    """
    Convert a KML file to a GPX object.
    Notes:
        * Only tested with KML files from a Pentax K-1 camera!
    """
    gpx = GPX()
    track = gpxpy.gpx.GPXTrack()
    gpx.tracks.append(track)

    segment = gpxpy.gpx.GPXTrackSegment()
    track.segments.append(segment)

    root = etree.parse(kml_file).getroot()
    namespaces = {'kml': root.nsmap.get(None)}

    for placemark in root.xpath('//kml:Placemark', namespaces=namespaces):
        dt = datetime_from_description(placemark, namespaces=namespaces)
        if not dt:
            continue

        coordinates = get_coordinates(placemark, namespaces=namespaces)
        if not coordinates:
            continue

        point = GPXTrackPoint(
            latitude=coordinates.latitude,
            longitude=coordinates.longitude,
            elevation=coordinates.altitude,
            time=dt,
        )
        segment.points.append(point)

    return gpx
