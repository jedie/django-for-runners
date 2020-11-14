"""
    created 30.05.2018 by Jens Diemer <opensource@jensdiemer.de>
    :copyleft: 2018 by the django-for-runners team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""
import collections
import logging
from decimal import Decimal as D

from django.contrib import admin
from django.contrib.admin.views.main import ChangeList
from django.template.response import TemplateResponse
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

# https://github.com/jedie/django-for-runners
from for_runners.admin.utils import BaseChangelistView
from for_runners.gpx_tools.humanize import convert_cash_values, human_distance, human_duration, human_seconds
from for_runners.models import EventLinkModel, EventModel
from for_runners.models.event import CostModel, ParticipationModel


log = logging.getLogger(__name__)


@admin.register(EventLinkModel)
class EventLinkModelAdmin(admin.ModelAdmin):
    list_display = ("event", "link_html")
    list_filter = ("event",)
    date_hierarchy = "event__start_date"
    search_fields = ("url", "text", "title", "event__name")


class LinkModelInline(admin.TabularInline):
    model = EventLinkModel
    extra = 2
    min_num = 0
    max_num = None
    fields = ("url", "text", "title")


class HasTracksFilter(admin.SimpleListFilter):
    title = _("has GPX tracks")
    parameter_name = "tracks"

    def lookups(self, request, model_admin):
        return (("y", _("yes")), ("n", _("no")))

    def queryset(self, request, queryset):
        if self.value() == "y":
            return queryset.exclude(participations__tracks__isnull=True)  # FIXME!
        if self.value() == "n":
            return queryset.filter(participations__tracks__isnull=True)  # FIXME!


class EventStatistics:
    KEY_DISTANCE = "_distance"
    KEY_DURATION = "_duration"

    def __init__(self):
        self.convert_map = {self.KEY_DISTANCE: human_distance, self.KEY_DURATION: human_duration}

    def get(self, events):
        raw_person_data = collections.defaultdict(collections.Counter)

        for event in events:
            # print(event)
            for participation in event.participations.all():
                # print(participation.person)
                participation_data = {
                    "_count": 1,
                    self.KEY_DISTANCE: participation.distance_km or 0,
                    self.KEY_DURATION: participation.get_duration_s() or 0,
                }

                for cost in participation.costs.all():
                    # print(cost)
                    participation_data[cost.name] = cost.amount

                raw_person_data[participation.person.username] += collections.Counter(participation_data)

        # turn defaultdict and counter to normal dict and convert some values:

        total_costs = collections.Counter()

        # pprint(raw_person_data)
        person_data = {}
        for username, counter_data in raw_person_data.items():
            user_data = []
            counter_data = dict(counter_data)
            for key, value in sorted(counter_data.items()):
                try:
                    func = self.convert_map[key]
                except KeyError:
                    pass
                else:
                    value = func(value)

                if key.startswith("_"):
                    # internal key
                    key = key[1:]
                else:
                    # costs item
                    # collect total costs:
                    total_costs += collections.Counter({"total": value, key: value})
                    # convert decimal field:
                    value = convert_cash_values(value)

                user_data.append((key, value))
            person_data[username] = user_data

        total_costs = dict(total_costs)
        total = total_costs.pop("total")  # add total as lates item
        total_costs = [(name, convert_cash_values(amount)) for name, amount in sorted(total_costs.items())]
        total_costs.append((_("total"), convert_cash_values(total)))

        # pprint(person_data)
        # pprint(total_costs)
        return person_data, total_costs


class StatisticsView(BaseChangelistView):

    template_name = "admin/for_runners/eventmodel/statistics.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        events = self.change_list.queryset  # filtered EventModel queryset form GpxModelChangeList
        # print("Events:", events.count())

        person_data, total_costs = EventStatistics().get(events)

        context.update(
            {
                "title": _("Event Statistics"),
                "person_data": person_data,
                "total_costs": total_costs,
                "user": self.request.user,
                "opts": EventModel._meta,
            }
        )
        return context


class EventModelChangeList(ChangeList):
    def get_results(self, request):
        super().get_results(request)

        view = StatisticsView.as_view()
        response = view(request, self)
        assert isinstance(response, TemplateResponse), f"Method {view} didn't return a TemplateResponse!"
        self.statistics = response.rendered_content


@admin.register(EventModel)
class EventModelAdmin(admin.ModelAdmin):
    def gpx_tracks_change_form_links(self, obj):
        """
        Link to GPX Tracks in object change view
        """
        html = []
        participations = obj.participations.all()
        for participation in participations:
            gpx_track = participation.track
            if gpx_track:
                change_url = gpx_track.get_admin_change_url()
                html.append(
                    '{username}: <a href="{url}">{length} <strong>{duration}</strong> {pace}</a>'.format(
                        username=participation.person.username,
                        url=change_url,
                        length=gpx_track.human_length_html(),
                        duration=gpx_track.human_duration_html(),
                        pace=gpx_track.human_pace(),
                    )
                )

        html = "<br>".join(html)
        html = mark_safe(html)
        return html

    gpx_tracks_change_form_links.short_description = _("GPX Tracks")

    def gpx_tracks_change_list_links(self, obj):
        """
        Link to GPX Tracks in admin change list
        """
        html = []
        participations = obj.participations.all()
        for participation in participations:
            gpx_track = participation.track
            if gpx_track:
                change_url = gpx_track.get_admin_change_url()
                html.append(
                    '<a href="{url}">{length} <strong>{duration}</strong> {pace}</a>'.format(
                        url=change_url,
                        length=gpx_track.human_length_html(),
                        duration=gpx_track.human_duration_html(),
                        pace=gpx_track.human_pace(),
                    )
                )

        html = "<br>".join(html)
        html = mark_safe(html)
        return html

    gpx_tracks_change_list_links.short_description = _("GPX Tracks")

    def participations(self, obj):
        html = []
        participations = obj.participations.all()
        for participation in participations:
            change_url = participation.get_admin_change_url()
            html.append(
                f'<a href="{change_url}">{participation.person.username} ({participation.get_human_distance()})</a>'
            )

        html = "<br>".join(html)
        html = mark_safe(html)
        return html

    participations.short_description = _("Participations")

    readonly_fields = ("gpx_tracks_change_form_links",)
    fieldsets = (
        (_("Event Name"), {"fields": (("no", "name", "start_date"), "discipline", "gpx_tracks_change_form_links")}),
    )

    list_display = (
        "verbose_name",
        "participations",
        "gpx_tracks_change_list_links",
        "links_html",
        "start_date",
        "discipline",
    )
    date_hierarchy = "start_date"
    list_filter = (HasTracksFilter, "participations__person")
    list_display_links = ("verbose_name",)
    search_fields = ("name",)
    inlines = [LinkModelInline]

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
    def start_date(self, obj):
        return obj.event.start_date

    start_date.admin_order_field = "event__start_date"

    def event_name(self, obj):
        return obj.event.short_name()

    event_name.short_description = _("Event")
    event_name.admin_order_field = "event"

    def human_duration(self, obj):
        if obj.duration:
            return human_seconds(obj.get_duration_s())

    human_duration.short_description = _("Duration")
    human_duration.admin_order_field = "duration"

    def pace(self, obj):
        pace_s = obj.get_pace_s()
        if pace_s:
            return f"{human_seconds(pace_s)} min/km"

    pace.short_description = _("Pace")

    def costs(self, obj):
        parts = []
        total = D("0.00")
        for entry in obj.costs.all():
            total += entry.amount
            parts.append(str(entry))

        if not parts:
            return ""
        elif len(parts) == 1:
            return f"{total:.2f}€"
        else:
            return f"{total:.2f}€ ({' '.join(parts)})"

    list_display = (
        "start_date",
        "event_name",
        "distance_km",
        "finisher_count",
        "person",
        "costs",
        "start_number",
        "human_duration",
        "pace",
    )
    list_display_links = ("event_name",)
    list_filter = ("person", "distance_km")
    date_hierarchy = "event__start_date"
    search_fields = ("person__username", "event__name", "event__start_date")
    inlines = [CostModelInline]
