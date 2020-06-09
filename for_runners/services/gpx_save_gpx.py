"""
    created 02.04.2019 by Jens Diemer <opensource@jensdiemer.de>
    :copyleft: 2019 by the django-for-runners team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import logging

from django.core.files.base import ContentFile


log = logging.getLogger(__name__)


def save_gpx_file(*, gpx_track, force=False):
    """
    Save the gpx track to disk by "attach" it to GpxModel.gpx_file

    :param gpx_track: for_runners.models.gpx.GpxModel instance
    :param gpxpy_instance: gpxpy.parser.GPXParser instance
    :param force: don't check if gpx track already exists
    :return: gpx
    """
    log.debug("Save gpx track to disk")

    if gpx_track.gpx_file:
        # gpx file already exists.
        if not force:
            log.info("Don't recreate existing gpx file")
            return

    content = ContentFile(gpx_track.gpx)

    # https://docs.djangoproject.com/en/2.0/ref/models/fields/#django.db.models.fields.files.FieldFile.save
    gpx_track.gpx_file.save(
        name="temp.gpx", content=content, save=False  # real file path will be set in self.get_gpx_upload_path()
    )
    log.debug(f"gpx file created: {gpx_track.gpx_file!r}")
