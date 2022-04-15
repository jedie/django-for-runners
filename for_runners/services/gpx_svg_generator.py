"""
    created 17.11.2018 by Jens Diemer <opensource@jensdiemer.de>
    :copyleft: 2018 by the django-for-runners team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""
import csv
import logging

from django.core.files.base import ContentFile

# https://github.com/jedie/django-for-runners
from for_runners.svg import gpx2svg_string


log = logging.getLogger(__name__)


def generate_svg(gpx_track, force=False):
    """
    Generate SVG and save it to the given GPXModel.

    :param gpx_track: for_runners.models.gpx.GpxModel instance
    :param gpxpy_instance: gpxpy.parser.GPXParser instance
    :param force: don't check if svg track already exists
    :return: svg
    """
    log.debug("Create SVG from GPX...")

    if gpx_track.track_svg.name:
        # svg image already exists.
        if not force:
            log.info("Don't recreate existing images")
            return

    log.debug("Create SVG from GPX...")
    gpxpy_instance = gpx_track.get_gpxpy_instance()
    svg_string = gpx2svg_string(gpxpy_instance)
    content = ContentFile(svg_string)

    # https://docs.djangoproject.com/en/2.0/ref/models/fields/#django.db.models.fields.files.FieldFile.save
    gpx_track.track_svg.save(
        name="temp.svg", content=content, save=False  # real file path will be set in self.get_svg_upload_path()
    )
    log.debug(f"SVG created: {gpx_track.track_svg!r}")
    gpx_track.save()


class CsvGenerator:
    """
    TODO: Replace with for_runners.admin.gpx_import_export.GpxModelResource
    """

    HEADER_DATE = "date"
    HEADER_NAME = "name"
    HEADER_EVENT = "event"
    HEADER_USER = "user"
    HEADER_LENGTH = "length (km)"
    HEADER_DURATION = "duration"
    HEADER_PACE = "pace"
    HEADER_HEART_RATE = "heart rate"
    HEADER_TEMPERATURE = "temperature"
    HEADER_WEATHER = "weather"
    HEADER_CREATOR = "creator"

    def __init__(self, *, csv_file, add_username=True):
        """
        :param csv_file: file object, opened for writing
        :param add_username: add the username as csv column
        """
        self.csv_file = csv_file
        self.add_username = add_username

        fieldnames = [
            self.HEADER_DATE,
            self.HEADER_NAME,
            self.HEADER_EVENT,
            self.HEADER_LENGTH,
            self.HEADER_DURATION,
            self.HEADER_PACE,
            self.HEADER_HEART_RATE,
            self.HEADER_TEMPERATURE,
            self.HEADER_WEATHER,
            self.HEADER_CREATOR,
        ]
        if add_username:
            fieldnames.insert(3, self.HEADER_USER)

        self.csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        self.csv_writer.writeheader()

    def add_gpx_track(self, track):
        if track.heart_rate_avg:
            heart_rate = "%i b/m" % track.heart_rate_avg
        else:
            heart_rate = ""

        if track.start_temperature:
            temperature = "%i°C" % round(track.start_temperature, 1)
            weather = track.start_weather_state
        else:
            temperature = ""
            weather = ""

        row = {
            self.HEADER_DATE: track.start_time.isoformat(),
            self.HEADER_NAME: track.short_name(start_time=False),
            self.HEADER_EVENT: "x" if track.participation else "",
            self.HEADER_LENGTH: round(track.length / 1000, 2),
            self.HEADER_DURATION: track.human_duration(),
            self.HEADER_PACE: track.human_pace(),
            self.HEADER_HEART_RATE: heart_rate,
            self.HEADER_TEMPERATURE: temperature,
            self.HEADER_WEATHER: weather,
            self.HEADER_CREATOR: track.creator,
        }
        if self.add_username:
            row[self.HEADER_USER] = track.tracked_by.username

        self.csv_writer.writerow(row)
