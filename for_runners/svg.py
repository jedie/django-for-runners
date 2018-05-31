import io
import math
from pathlib import Path

import svgwrite

# https://github.com/jedie/django-for-runners
# Django CMS Tools
from for_runners.gpx_tools.garmin2gpxpy import garmin2gpxpy


def gpx2svg(gpxpy_instance):
    lat_list = []
    lon_list = []

    for track in gpxpy_instance.tracks:
        for segment in track.segments:
            for point in segment.points:
                # print('Point at ({0},{1}) -> {2}'.format(point.latitude, point.longitude, point.elevation))
                lat_list.append(point.latitude)
                lon_list.append(point.longitude)

    # print(lat)
    # print(lon)

    lon_min = min(lon_list)
    lat_min = min(lat_list)
    lon_max = max(lon_list)
    lat_max = max(lat_list)

    print(
        "lon",
        lon_min,
        lon_max,
        "lat",
        lat_min,
        lat_max,
    )

    lat_area = lat_max - lat_min
    lon_area = lon_max - lon_min
    if lon_area > lat_area:
        aspect = lat_area / lon_area
    else:
        aspect = lon_area / lat_area
    print("areas:", lat_area, lon_area, "aspect:", aspect)

    ############################################################################################

    border = 5

    # the minimum distance between two points
    min_distance = 0.2

    total_size_x = 100
    total_size_y = 100

    print("total_size:", total_size_x, total_size_y)

    drawing = svgwrite.Drawing(size=(total_size_x, total_size_y), profile='tiny')
    drawing.add(drawing.rect(insert=(0, 0), size=(total_size_x, total_size_y), fill='#000000'))
    drawing.add(drawing.rect(insert=(1, 1), size=(total_size_x - 2, total_size_y - 2), fill='#ffffff'))
    lines = drawing.add(drawing.g(stroke_width=1, stroke='blue', fill='none'))

    lines_size_x = total_size_x - (border * 2)
    lines_size_y = total_size_y - (border * 2)
    print("lines_size:", lines_size_x, lines_size_y)

    scale_x = lines_size_x / lon_area * aspect
    scale_y = lines_size_y / lat_area

    print("scale:", scale_x, scale_y)

    max_x = lon_area * scale_x
    max_y = lat_area * scale_y
    print("max:", max_x, max_y)

    offset_x = border + ((lines_size_x - max_x) / 2)
    offset_y = border + ((lines_size_y - max_y) / 2)
    print("offset:", offset_x, offset_y)

    # x_list = []
    # y_list = []

    old_x = None
    old_y = None
    for lon, lat in zip(lon_list, lat_list):
        x = ((lon - lon_min) * scale_x) + offset_x
        y = ((lat - lat_min) * scale_y) + offset_y

        y = y * -1 + total_size_y  # mirror the x-axis

        # x_list.append(x)
        # y_list.append(y)

        if old_x is not None:
            if abs(old_x - x) < min_distance:
                continue
            if abs(old_y - y) < min_distance:
                continue
            lines.add(drawing.line(start=(old_x, old_y), end=(x, y)))

        old_x = x
        old_y = y

    # print(min(x_list), max(x_list), min(y_list), max(y_list))

    return drawing


def gpx2svg_file(gpxpy_instance, svg_filename, pretty=False):
    drawing = gpx2svg(gpxpy_instance)
    drawing.saveas(svg_filename, pretty=pretty)


def gpx2svg_string(gpxpy_instance, pretty=False):
    drawing = gpx2svg(gpxpy_instance)
    fileobj = io.StringIO()
    drawing.write(fileobj, pretty=False)
    return fileobj.getvalue()


