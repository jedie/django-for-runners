"""
    created 30.05.2018 by Jens Diemer <opensource@jensdiemer.de>
    :copyleft: 2018 by the django-for-runners team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import logging

from django.contrib import admin

# https://github.com/jedie/django-for-runners
from for_runners.models import DistanceModel


log = logging.getLogger(__name__)


@admin.register(DistanceModel)
class DistanceModelAdmin(admin.ModelAdmin):
    list_display = ("get_human_distance", "get_human_variance", "get_human_variance_as_length", "get_human_min_max")
    list_display_links = ("get_human_distance",)
