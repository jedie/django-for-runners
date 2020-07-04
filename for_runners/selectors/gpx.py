"""
    created 17.11.2018 by Jens Diemer <opensource@jensdiemer.de>
    :copyleft: 2018 by the django-for-runners team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import logging

from django.contrib.auth import get_user_model
from django.db.models import Count

# https://github.com/jedie/django-for-runners
from for_runners.models import GpxModel


log = logging.getLogger(__name__)


def gpx_users():
    User = get_user_model()
    qs = User.objects.annotate(num_tracks=Count("gpxmodel_createby"))
    qs = qs.filter(num_tracks__gt=0)
    return qs


def gpx_tracks(has_gpx=True):
    qs = GpxModel.objects.all()
    if has_gpx:
        qs = qs.exclude(gpx="")
    return qs


def gpx_user_tracks(user, has_gpx=True):
    qs = gpx_tracks(has_gpx=has_gpx)
    qs = qs.filter(tracked_by=user)
    return qs
