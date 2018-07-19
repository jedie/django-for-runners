"""
    created 30.05.2018 by Jens Diemer <opensource@jensdiemer.de>
    :copyleft: 2018 by the django-for-runners team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import logging

from django.contrib import admin
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

# https://github.com/jedie/django-for-runners
from for_runners.gpx_tools.humanize import human_seconds
from for_runners.models import EventLinkModel, EventModel
from for_runners.models.event import CostModel, ParticipationModel

log = logging.getLogger(__name__)


@admin.register(EventLinkModel)
class EventLinkModelAdmin(admin.ModelAdmin):
    pass


class LinkModelInline(admin.TabularInline):
    model = EventLinkModel
    extra = 2
    min_num = 0
    max_num = None
    fields = (
        'url',
        'text',
        'title',
    )


class HasTracksFilter(admin.SimpleListFilter):
    title = _('has GPX tracks')
    parameter_name = "tracks"

    def lookups(self, request, model_admin):
        return (
            ('y', _('yes')),
            ('n', _('no')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'y':
            return queryset.exclude(tracks__isnull=True)
        if self.value() == 'n':
            return queryset.filter(tracks__isnull=True)


@admin.register(EventModel)
class EventModelAdmin(admin.ModelAdmin):

    def participations(self, obj):
        html = []
        participations = obj.participations.all()
        for participation in participations:
            html.append(participation.person.username)
        html = "<br>".join(html)
        html = mark_safe(html)
        return html
    participations.short_description = _("Participations")

    list_display = ("verbose_name", "participations", "links_html", "start_date", "discipline")
    date_hierarchy = "start_date"
    list_filter = (HasTracksFilter,)
    list_display_links = ("verbose_name",)
    inlines = [
        LinkModelInline,
    ]


class CostModelInline(admin.TabularInline):
    model = CostModel
    extra = 2
    min_num = 0
    max_num = None


@admin.register(ParticipationModel)
class ParticipationModelAdmin(admin.ModelAdmin):

    def human_duration(self, obj):
        if obj.duration:
            return human_seconds(obj.get_duration_s())
    human_duration.short_description = _("Duration")
    human_duration.admin_order_field = "duration"

    def pace(self, obj):
        pace_s = obj.get_pace_s()
        if pace_s:
            return "%s min/km" % human_seconds(pace_s)
    pace.short_description = _("Pace")

    list_display = ("event", "distance_km", "finisher_count", "person", "start_number", "human_duration", "pace")
    list_filter = ("person", "distance_km")
    date_hierarchy = "event__start_date"
    search_fields = (
        "person__username",
        "event__name",
        "event__start_date",
    )
    inlines = [
        CostModelInline,
    ]
