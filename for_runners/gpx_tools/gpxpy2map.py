"""
    created 30.05.2018 by Jens Diemer <opensource@jensdiemer.de>
    :copyleft: 2018 by the django-for-runners team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""
import asyncio
import logging

import matplotlib.pyplot as plt  # https://pypi.org/project/matplotlib/
from django.conf import settings
from for_runners.gpx import get_2d_coordinate_list

try:
    import geotiler  # https://wrobell.dcmod.org/geotiler/
except SyntaxError:
    # geotiler needs Python 3.6 :(
    # https://github.com/wrobell/geotiler/issues/20
    geotiler = None

log = logging.getLogger(__name__)


def generate_map(gpxpy_instance):

    lat, lon = get_2d_coordinate_list(gpxpy_instance)
    # print(lat)
    # print(lon)

    lon_min = min(lon)
    lat_min = min(lat)
    lon_max = max(lon)
    lat_max = max(lat)

    print(lon_min, lon_max, lat_min, lat_max)

    width = lat_max - lat_min
    height = lon_max - lon_min
    print("width", width, "height", height)

    aspect = width / height  # 0.8114047529717512 -> 1280 1039
    print("aspect", aspect)

    size_x = 1280
    size_y = int(round(size_x * aspect, 0))
    print(size_x, size_y)

    fig = plt.figure()
    ax = fig.add_subplot(111)

    image = None
    if geotiler is None:
        log.error("Can't use geotiler!")
    elif settings.MAP_DOWNLOAD:
        log.info("Download map via geotiler...")
        map = geotiler.Map(extent=(lon_min, lat_min, lon_max, lat_max), size=(size_x, size_y))
        lon_min2, lat_min2, lon_max2, lat_max2 = map.extent

        log.info("Render geotiler map...")
        asyncio.set_event_loop(asyncio.new_event_loop())  # Fix: There is no current event loop in thread 'Thread-1'.
        image = geotiler.render_map(map)
        log.info("Geotiler map rendered, OK")

        ax.imshow(image, extent=(lon_min2, lon_max2, lat_min2, lat_max2), aspect='auto', alpha=0.4)
    else:
        log.info("Skip downloading map via geotiler, because settings.MAP_DOWNLOAD != True")

    plt.plot(lon, lat, color="#000000", lw=0.5, alpha=0.9)

    time_bounds = gpxpy_instance.get_time_bounds()
    plt.title(time_bounds.start_time)

    plt.xlabel('latitude')
    plt.ylabel('longitude')

    return image, plt


# gpx = garmin2gpxpy(filepath=FILEPATH)
#
# print("length: %.2fm" % gpx.length_3d())
# print("duration: %.2fs" % gpx.get_duration())
# print("uphill_downhill:", gpx.get_uphill_downhill())
#
# time_bounds = gpx.get_time_bounds()
# print(time_bounds)
#
# image, plt = generate_map(gpx)
#
# image.save('test_map.png')
# plt.savefig('test.png', bbox_inches='tight')
# # plt.show()
