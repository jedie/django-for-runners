import io
import logging

import svgwrite
from for_runners.exceptions import GpxDataError
from for_runners.gpx import get_2d_coordinate_list

log = logging.getLogger(__name__)


def gpx2svg(gpxpy_instance):
    """
    Optimize output with:

        * simplify(max_distance)
        * reduce_points(min_distance)

    FIXME:
        * Use correct World Geodetic System: WGS 84 calculations ;)
    """
    lat_list, lon_list = get_2d_coordinate_list(gpxpy_instance)

    lon_min = min(lon_list)
    lat_min = min(lat_list)
    lon_max = max(lon_list)
    lat_max = max(lat_list)

    log.debug("lon %s-%s lat %s-%s", lon_min, lon_max, lat_min, lat_max)

    lat_area = lat_max - lat_min
    lon_area = lon_max - lon_min
    if lon_area > lat_area:
        aspect = lat_area / lon_area
    else:
        aspect = lon_area / lat_area
    log.debug("Areas: %s,%s Aspect: %s", lat_area, lon_area, aspect)

    ############################################################################################

    border = 5

    # the minimum distance between two points
    min_distance = 0.2

    total_size_x = 100
    total_size_y = 100

    log.debug("total_size: %ix%i", total_size_x, total_size_y)

    drawing = svgwrite.Drawing(size=(total_size_x, total_size_y), profile='tiny')
    drawing.add(drawing.rect(insert=(0, 0), size=(total_size_x, total_size_y), fill='#000000'))
    drawing.add(drawing.rect(insert=(1, 1), size=(total_size_x - 2, total_size_y - 2), fill='#ffffff'))
    lines = drawing.add(drawing.g(stroke_width=1, stroke='blue', fill='none'))

    lines_size_x = total_size_x - (border * 2)
    lines_size_y = total_size_y - (border * 2)
    log.debug("lines_size: %ix%i", lines_size_x, lines_size_y)

    scale_x = lines_size_x / lon_area * aspect
    scale_y = lines_size_y / lat_area

    log.debug("scale: %ix%i", scale_x, scale_y)

    max_x = lon_area * scale_x
    max_y = lat_area * scale_y
    log.debug("max: %ix%i", max_x, max_y)

    offset_x = border + ((lines_size_x - max_x) / 2)
    offset_y = border + ((lines_size_y - max_y) / 2)
    log.debug("offset: %ix%i", offset_x, offset_y)

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

    # log.debug(min(x_list), max(x_list), min(y_list), max(y_list))

    return drawing


def gpx2svg_file(gpxpy_instance, svg_filename, pretty=False):
    drawing = gpx2svg(gpxpy_instance)
    drawing.saveas(svg_filename, pretty=pretty)


def gpx2svg_string(gpxpy_instance, pretty=False):
    drawing = gpx2svg(gpxpy_instance)
    fileobj = io.StringIO()
    drawing.write(fileobj, pretty=pretty)
    return fileobj.getvalue().strip()
