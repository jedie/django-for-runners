"""
    created 30.05.2018 by Jens Diemer <opensource@jensdiemer.de>
    :copyleft: 2018 by the django-for-runners team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""
import logging

from django.db import IntegrityError, models

# https://github.com/jedie/django-for-runners
from for_runners.gpx import get_identifier, parse_gpx

log = logging.getLogger(__name__)


class GpxModelQuerySet(models.QuerySet):

    def filter_by_identifier(self, identifier):
        """
        :param identifier: 'Identifier' namedtuple created here: for_runners.gpx.get_identifier
        """
        return self.filter(
            start_time=identifier.start_time,
            finish_time=identifier.finish_time,
            start_latitude=identifier.start_lat,
            start_longitude=identifier.start_lon,
            finish_latitude=identifier.finish_lat,
            finish_longitude=identifier.finish_lon,
        )


class BaseGpxModelManager(models.Manager):

    def get_queryset(self):
        return GpxModelQuerySet(self.model, using=self._db)

    def add_gpx(self, gpx_content, user):
        """
        Create a new for_runners.models.GpxModel entry

        :param gpx_content: String content of the new gpx file
        :return: GpxModel instance
        """
        gpxpy_instance = parse_gpx(gpx_content)
        identifier = get_identifier(gpxpy_instance)
        qs = self.get_queryset().filter_by_identifier(identifier)
        if qs.exists():
            log.warning("Track with same start time, latitude, longitude already exists!")
            qs = qs.filter(tracked_by=user)
            if qs.exists():
                gpx = qs.get()
                raise IntegrityError(
                    "GPX track already exists: %s" % gpx
                )

        instance = self.create(
            gpx=gpx_content,
            tracked_by=user,
        )
        return instance


GpxModelManager = BaseGpxModelManager.from_queryset(GpxModelQuerySet)
