"""
    created 17.11.2018 by Jens Diemer <opensource@jensdiemer.de>
    :copyleft: 2018 by the django-for-runners team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

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
    if gpx_track.track_svg:
        # svg image already exists.
        if not force:
            # Don't recreate existing images
            return

    log.debug("Create SVG from GPX...")
    gpxpy_instance = gpx_track.get_gpxpy_instance()
    svg_string = gpx2svg_string(gpxpy_instance)
    content = ContentFile(svg_string)

    # https://docs.djangoproject.com/en/2.0/ref/models/fields/#django.db.models.fields.files.FieldFile.save
    svg = gpx_track.track_svg.save(
        name="temp.svg",  # real file path will be set in self.get_svg_upload_path()
        content=content,
        save=False
    )
    log.debug("SVG created: %r" % svg)

    return svg
