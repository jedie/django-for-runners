"""
    created 25.08.2019 by Jens Diemer <opensource@jensdiemer.de>
    :copyleft: 2019 by the django-for-runners team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import logging

from django.db import IntegrityError, transaction
# https://github.com/jedie/django-tools
from django_tools.unittest_utils.assertments import assert_is_dir, assert_is_file
from gpxpy.gpx import GPXException

# https://github.com/jedie/django-for-runners
from for_runners.exceptions import GpxDataError
from for_runners.gpx import get_identifier, parse_gpx
from for_runners.models import GpxModel


log = logging.getLogger(__name__)


def add_gpx(*, gpx_content, user):
    """
    Create a new for_runners.models.GpxModel entry

    :param gpx_content: String content of the new gpx file
    :return: GpxModel instance
    """
    try:
        gpxpy_instance = parse_gpx(gpx_content)
    except GPXException as err:
        log.exception(f"Invalid GPX Data: {err}")
        return

    identifier = get_identifier(gpxpy_instance)

    try:
        instance = GpxModel.objects.get_by_identifier(identifier)
    except GpxModel.DoesNotExist:
        log.debug("Create new track for user: %s", user)
        instance = GpxModel.objects.create(gpx=gpx_content, tracked_by=user)
        return instance
    else:
        if instance.tracked_by != user:
            log.error("Skip existing track: %s (Tracked by: %s)", instance, instance.tracked_by)
        else:
            log.info("Skip existing track: %s", instance)
        return


def add_from_file(*, gpx_file_file_path, user):
    """
    Read content from gpx file <gpx_files_file_path> and add to <user>
    """
    assert_is_file(gpx_file_file_path)

    log.info(f'Add GPX file: {gpx_file_file_path}')
    with gpx_file_file_path.open("r") as f:
        gpx_content = f.read()

    return add_gpx(gpx_content=gpx_content, user=user)


def add_from_files(*, gpx_files_file_path, user, skip_errors=True):
    """
    Add all *.gpx files from <gpx_files_file_path> to <user>
    """
    assert_is_dir(gpx_files_file_path)

    gpx_files = gpx_files_file_path.glob("**/*.gpx")
    for gpx_file_file_path in sorted(gpx_files):
        try:
            with transaction.atomic():
                instance = add_from_file(gpx_file_file_path=gpx_file_file_path, user=user)
        except (IntegrityError, GpxDataError) as err:
            log.error("Skip .gpx file: %s", err)
            if not skip_errors:
                raise
        else:
            if instance:
                yield instance
