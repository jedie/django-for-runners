"""
    created 19.07.2018 by Jens Diemer <opensource@jensdiemer.de>
    :copyleft: 2018 by the django-for-runners team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""
from django.contrib import admin

from for_runners.admin.discipline import DisciplineModelAdmin
from for_runners.admin.distance import DistanceModelAdmin
from for_runners.admin.event import EventLinkModelAdmin, EventModelAdmin, ParticipationModelAdmin
from for_runners.admin.gpx import GpxModelAdmin
from for_runners.admin.utils import export_as_json

# Make export actions available site-wide
admin.site.add_action(export_as_json, 'export_selected_as_json')
