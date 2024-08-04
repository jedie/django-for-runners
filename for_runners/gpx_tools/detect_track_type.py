import logging
from enum import StrEnum, auto
from typing import BinaryIO

from lxml import etree


log = logging.getLogger(__name__)


class TrackType(StrEnum):
    UNKNOWN = auto()
    GPX = auto()
    KML = auto()


def detect_type(content_file: BinaryIO):
    """
    Returns a enum value of the track type:
    * TrackType.UNKNOWN
    * TrackType.GPX
    * TrackType.KML
    """
    try:
        root = etree.parse(content_file).getroot()
    except etree.XMLSyntaxError as err:
        log.exception('Failed to parse XML content: %s', err)
        return TrackType.UNKNOWN

    root_tag = root.tag

    if root_tag == 'gpx' or root_tag.endswith('}gpx'):
        return TrackType.GPX
    if root_tag == 'kml' or root_tag.endswith('}kml'):
        return TrackType.KML

    return TrackType.UNKNOWN
