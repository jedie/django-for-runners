"""
    created 30.05.2018 by Jens Diemer <opensource@jensdiemer.de>
    :copyleft: 2018 by the django-for-runners team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""
import logging

from django.db import models


log = logging.getLogger(__name__)


class GpxModelQuerySet(models.QuerySet):
    def get_by_identifier(self, identifier):
        """
        :param identifier: 'Identifier' namedtuple created here: for_runners.gpx.get_identifier
        """
        return self.get(
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


GpxModelManager = BaseGpxModelManager.from_queryset(GpxModelQuerySet)
