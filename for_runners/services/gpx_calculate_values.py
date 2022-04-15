"""
    created 02.04.2019 by Jens Diemer <opensource@jensdiemer.de>
    :copyleft: 2018-2019 by the django-for-runners team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import logging
import statistics

# https://github.com/jedie/django-for-runners
from for_runners.geo import reverse_geo
from for_runners.gpx import get_extension_data, get_identifier
from for_runners.models import DistanceModel
from for_runners.weather import NoWeatherData, meta_weather_com


log = logging.getLogger(__name__)


def calculate_values(*, gpx_track):
    if not gpx_track.gpx:
        return

    gpxpy_instance = gpx_track.get_gpxpy_instance()
    gpx_track.points_no = gpxpy_instance.get_points_no()
    gpx_track.length = gpxpy_instance.length_3d()

    try:
        ideal_distances_qs = DistanceModel.objects.filter(
            min_distance_m__lte=gpx_track.length, max_distance_m__gte=gpx_track.length
        )
    except DistanceModel.DoesNotExist:
        pass
    else:
        ideal_distance_count = ideal_distances_qs.count()
        if ideal_distance_count > 1:
            log.error("Found more the one ideal distances for %i Meters", gpx_track.length)
            ideal_distances_qs = ideal_distances_qs.order_by("distance_km")
            ideal_distance = ideal_distances_qs[0]
        elif ideal_distance_count == 1:
            ideal_distance = ideal_distances_qs.get()
        else:
            ideal_distance = None

        if ideal_distance:
            gpx_track.ideal_distance = ideal_distance
            log.debug("Set ideal distance to %s", gpx_track.ideal_distance)

    # e.g: GPX without a track return 0
    duration = gpxpy_instance.get_duration()
    if duration:
        gpx_track.duration_s = duration
        gpx_track.calc_pace()

    uphill_downhill = gpxpy_instance.get_uphill_downhill()
    gpx_track.uphill = uphill_downhill.uphill
    gpx_track.downhill = uphill_downhill.downhill

    elevation_extremes = gpxpy_instance.get_elevation_extremes()
    gpx_track.min_elevation = elevation_extremes.minimum
    gpx_track.max_elevation = elevation_extremes.maximum

    identifier = get_identifier(gpxpy_instance)

    gpx_track.start_time = identifier.start_time
    gpx_track.finish_time = identifier.finish_time
    gpx_track.start_latitude = identifier.start_lat
    gpx_track.start_longitude = identifier.start_lon
    gpx_track.finish_latitude = identifier.finish_lat
    gpx_track.finish_longitude = identifier.finish_lon

    if not gpx_track.start_temperature:
        try:
            temperature, weather_state = meta_weather_com.coordinates2weather(
                gpx_track.start_latitude,
                gpx_track.start_longitude,
                date=gpx_track.start_time,
                max_seconds=gpx_track.duration_s,
            )
        except NoWeatherData:
            log.error("No weather data for start.")
        else:
            gpx_track.start_temperature = temperature
            gpx_track.start_weather_state = weather_state

    if not gpx_track.finish_temperature:
        try:
            temperature, weather_state = meta_weather_com.coordinates2weather(
                gpx_track.finish_latitude,
                gpx_track.finish_longitude,
                date=gpx_track.finish_time,
                max_seconds=gpx_track.duration_s,
            )
        except NoWeatherData:
            log.error("No weather data for finish.")
        else:
            gpx_track.finish_temperature = temperature
            gpx_track.finish_weather_state = weather_state

    if not gpx_track.full_start_address:
        try:
            start_address = reverse_geo(gpx_track.start_latitude, gpx_track.start_longitude)
        except Exception as err:
            # e.g.: geopy.exc.GeocoderTimedOut: Service timed out
            log.error(f"Can't reverse geo: {err}")
        else:
            gpx_track.short_start_address = start_address.short
            gpx_track.full_start_address = start_address.full

    if not gpx_track.full_finish_address:
        try:
            finish_address = reverse_geo(gpx_track.finish_latitude, gpx_track.finish_longitude)
        except Exception as err:
            # e.g.: geopy.exc.GeocoderTimedOut: Service timed out
            log.error(f"Can't reverse geo: {err}")
        else:
            gpx_track.short_finish_address = finish_address.short
            gpx_track.full_finish_address = finish_address.full

    # TODO: Handle other extensions, too.
    # Garmin containes also 'cad'
    extension_data = get_extension_data(gpxpy_instance)
    if extension_data is not None and "hr" in extension_data:
        heart_rates = extension_data["hr"]
        gpx_track.heart_rate_min = min(heart_rates)
        gpx_track.heart_rate_avg = statistics.median(heart_rates)
        gpx_track.heart_rate_max = max(heart_rates)

    if not gpx_track.creator:
        gpx_track.creator = gpxpy_instance.creator
