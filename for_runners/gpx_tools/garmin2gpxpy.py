"""

    Convert a Garmin connect GPX file to a gpxpy instance

    work-a-round until https://github.com/tkrajina/gpxpy/issues/115#issuecomment-392798245 fixed
"""

from pathlib import Path

import gpxpy.gpx
from lxml import etree


def garmin2gpxpy(content):
    gpx = gpxpy.gpx.GPX()
    gpx.tracks.append(gpxpy.gpx.GPXTrack())
    gpx.tracks[0].segments.append(gpxpy.gpx.GPXTrackSegment())

    NS = {'ns': 'http://www.topografix.com/GPX/1/1'}

    if isinstance(content, str):
        content = content.encode("utf-8")

    tree = etree.fromstring(content)

    for track_point in tree.xpath('//ns:trk/ns:trkseg/ns:trkpt', namespaces=NS):
        latitude = float(track_point.get("lat"))
        longitude = float(track_point.get("lon"))

        elevation = track_point.xpath('ns:ele/text()', namespaces=NS)
        elevation = float(elevation[0])

        point_time = track_point.xpath('ns:time/text()', namespaces=NS)[0]
        # e.g.: 2018-04-28T14:30:50.000Z
        point_time = gpxpy.gpxfield.parse_time(point_time)

        # print('latitude', latitude, 'longitude', longitude, "elevation", elevation)
        point = gpxpy.gpx.GPXTrackPoint(latitude=latitude, longitude=longitude, elevation=elevation, time=point_time)
        gpx.tracks[0].segments[0].points.append(point)

    return gpx

