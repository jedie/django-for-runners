"""
    created 25.08.2019 by Jens Diemer <opensource@jensdiemer.de>
    :copyleft: 2019 by the django-for-runners team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import logging
import os

import gpxpy
from django.db import IntegrityError

# https://github.com/jedie/django-tools
from django_tools.unittest_utils.assertments import assert_is_dir, assert_is_file
from gpxpy.gpx import GPX

# https://github.com/jedie/django-for-runners
from for_runners.exceptions import GpxDataError
from for_runners.gpx import get_identifier
from for_runners.gpx_tools.kml import kml2gpx
from for_runners.models import GpxModel


log = logging.getLogger(__name__)


def add_gpx(*, gpx: GPX, user) -> GpxModel | None:
    """
    Create a new for_runners.models.GpxModel entry

    :param gpx_content: String content of the new gpx file
    :return: GpxModel instance
    """
    identifier = get_identifier(gpx)
    log.info(f'{identifier=}')

    log.error(str(list(GpxModel.objects.values_list('tracked_by', 'start_time', 'start_latitude'))))

    try:
        instance: GpxModel = GpxModel.objects.get_by_identifier(identifier)
    except GpxModel.DoesNotExist:
        log.debug("Create new track for user: %s", user)
        gpx_content = gpx.to_xml()
        instance = GpxModel.objects.create(gpx=gpx_content, tracked_by=user)
        return instance
    else:
        if instance.tracked_by != user:
            log.error("Skip existing track: %s (Tracked by: %s)", instance, instance.tracked_by)
        else:
            log.info("Skip existing track: %s %s", instance, instance.get_identifier())
        return


def add_from_file(*, track_path, user):
    """
    Read content from gpx file <gpx_files_file_path> and add to <user>
    """
    assert_is_file(track_path)

    file_suffix = track_path.suffix.lower()
    log.info(f'Add track file: {track_path} ({file_suffix=})')
    if file_suffix == '.kml':
        gpx: GPX = kml2gpx(track_path)
    elif file_suffix == '.gpx':
        gpx_content = track_path.read_text()
        gpx: GPX = gpxpy.parse(gpx_content)
    else:
        raise GpxDataError(f"Unknown file extension: {track_path}")

    return add_gpx(gpx=gpx, user=user)


def multi_glob(path, *, extensions: tuple):
    with os.scandir(path) as it:
        for entry in it:
            if entry.is_file():
                file_path = path / entry.name
                if file_path.suffix.lower() in extensions:
                    yield file_path


def add_from_files(*, tracks_path, user, skip_errors=True):
    """
    Add all *.gpx files from <gpx_files_file_path> to <user>
    """
    assert_is_dir(tracks_path)

    tracks = multi_glob(tracks_path, extensions=('.gpx', '.kml'))

    for track_path in sorted(tracks):
        try:
            instance = add_from_file(track_path=track_path, user=user)
        except (IntegrityError, GpxDataError) as err:
            log.exception("Skip %s: %s", track_path, err)
            if not skip_errors:
                raise
        else:
            if instance:
                yield instance
