"""
    created 30.05.2018 by Jens Diemer <opensource@jensdiemer.de>
    :copyleft: 2018 by the django-for-runners team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""
import collections
import logging
from pprint import pprint

from django.contrib import admin
from django.contrib.admin.views.main import ChangeList
from django.db import models
from django.template.response import TemplateResponse
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

# https://github.com/jedie/django-for-runners
from for_runners.admin.utils import BaseChangelistView
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
            return queryset.exclude(participations__tracks__isnull=True)  # FIXME!
        if self.value() == 'n':
            return queryset.filter(participations__tracks__isnull=True)  # FIXME!


class StatisticsView(BaseChangelistView):
    template_name = "admin/for_runners/eventmodel/statistics.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        events = self.change_list.queryset  # filtered EventModel queryset form GpxModelChangeList
        # print("Events:", events.count())

        person_data = collections.defaultdict(collections.Counter)

        for event in events:
            # print(event)
            for participation in event.participations.all():
                # print(participation.person)
                participation_data = {
                    "count": 1,
                    "distance_km": participation.distance_km or 0,
                    "duration": participation.get_duration_s() or 0,
                }

                for cost in participation.costs.all():
                    # print(cost)
                    participation_data[cost.name] = cost.amount

                person_data[participation.person.username] += collections.Counter(participation_data)

        # turn defaultdict and counter to normal dict:
        person_data = dict([(key, dict(value)) for key, value in person_data.items()])
        # pprint(person_data)

        context.update({
            "title": _("Event Statistics"),
            "person_data": person_data,
            "user": self.request.user,
            "opts": EventModel._meta,
        })
        return context


class EventModelChangeList(ChangeList):

    def get_results(self, request):
        super().get_results(request)

        view = StatisticsView.as_view()
        response = view(request, self)
        assert isinstance(response, TemplateResponse), "Method %s didn't return a TemplateResponse!" % view
        self.statistics = response.rendered_content


@admin.register(EventModel)
class EventModelAdmin(admin.ModelAdmin):

    def participations(self, obj):
        html = []
        participations = obj.participations.all()
        for participation in participations:
            html.append("%s (%s)" % (
                participation.person.username,
                participation.get_human_distance(),
            ))
        html = "<br>".join(html)
        html = mark_safe(html)
        return html
    participations.short_description = _("Participations")

    list_display = ("verbose_name", "participations", "links_html", "start_date", "discipline")
    date_hierarchy = "start_date"
    list_filter = (HasTracksFilter, "participations__person")
    list_display_links = ("verbose_name",)
    search_fields = ("name",)
    inlines = [
        LinkModelInline,
    ]

    def get_changelist(self, request, **kwargs):
        """
        Returns the ChangeList class for use on the changelist page.
        """
        return EventModelChangeList


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
