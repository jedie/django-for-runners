"""
    created 30.05.2018 by Jens Diemer <opensource@jensdiemer.de>
    :copyleft: 2018 by the django-for-runners team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""
import asyncio

import geotiler  # https://wrobell.dcmod.org/geotiler/
import matplotlib.pyplot as plt  # https://pypi.org/project/matplotlib/


def generate_map(gpxpy_instance):
    lat = []
    lon = []
    for track in gpxpy_instance.tracks:
        for segment in track.segments:
            for point in segment.points:
                # print('Point at ({0},{1}) -> {2}'.format(point.latitude, point.longitude, point.elevation))
                lat.append(point.latitude)
                lon.append(point.longitude)

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

    map = geotiler.Map(extent=(lon_min, lat_min, lon_max, lat_max), size=(size_x, size_y))
    lon_min2, lat_min2, lon_max2, lat_max2 = map.extent

    print("Render map...")
    asyncio.set_event_loop(asyncio.new_event_loop())  # Fix: There is no current event loop in thread 'Thread-1'.
    image = geotiler.render_map(map)
    print("OK")

    ax = plt.subplot(111)
    ax.imshow(image, extent=(lon_min2, lon_max2, lat_min2, lat_max2), aspect='auto', alpha=0.4)

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
