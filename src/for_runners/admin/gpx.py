"""
    created 30.05.2018 by Jens Diemer <opensource@jensdiemer.de>
    :copyleft: 2018 by the django-for-runners team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""
import collections
import logging
import math
import statistics
from pprint import pprint

from django import forms
from django.conf.urls import url
from django.contrib import admin, messages
from django.contrib.admin.views.main import ChangeList
from django.db import IntegrityError, NotSupportedError, models
from django.db.models import Avg, Max, Min
from django.http import HttpResponseRedirect
from django.template.loader import render_to_string
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.views import generic
# https://github.com/jedie/django-tools
from django_tools.decorators import display_admin_error
from import_export.admin import ExportMixin

# https://github.com/jedie/django-for-runners
from for_runners import constants
from for_runners.admin.gpx_import_export import GpxModelResource
from for_runners.admin.utils import BaseChangelistView, BaseFormChangelistView
from for_runners.exceptions import GpxDataError
from for_runners.forms import INITIAL_DISTANCE, DistanceStatisticsForm, UploadGpxFileForm
from for_runners.gpx import add_extension_data, get_2d_coordinate_list, iter_distance, iter_points
from for_runners.models import GpxModel
from for_runners.services.gpx_svg_generator import generate_svg


log = logging.getLogger(__name__)

STATISTICS_CHOICES = (
    (constants.DISPLAY_DISTANCE_PACE_KEY, _("Distance/Pace")),
    (constants.DISPLAY_PACE_DURATION, _("Pace/Duration")),
    (constants.DISPLAY_GPX_INFO, _("GPX info")),
    (constants.DISPLAY_GPX_METADATA, _("GPX metadata")),
)
assert len(dict(STATISTICS_CHOICES)) == len(STATISTICS_CHOICES), "Double keys?!?"


class UploadGpxFileView(generic.FormView):
    template_name = "for_runners/upload_gpx_file.html"
    form_class = UploadGpxFileForm
    success_url = "../"  # FIXME

    def post(self, request, *args, **kwargs):
        user = request.user
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        files = request.FILES.getlist("gpx_files")
        if form.is_valid():
            log.debug("files: %r", files)
            for f in files:
                messages.info(request, f"Process {f.name}...")

                content = f.file.read()
                log.debug("raw content......: %s", repr(content)[:100])
                content = content.decode("utf-8")
                log.debug("decoded content..: %s", repr(content)[:100])

                try:
                    try:
                        gpx = GpxModel.objects.create(gpx=content, tracked_by=user)
                    except IntegrityError as err:
                        # catch: UNIQUE constraint failed
                        # give a better error message
                        messages.error(request, f"Error process GPX data: {err}")
                        continue
                except GpxDataError as err:
                    messages.error(request, f"Error process GPX data: {err}")
                else:
                    messages.success(request, f"Created: {gpx}")

                    # redirect to change view:
                    self.success_url = gpx.get_admin_change_url()

            return self.form_valid(form)
        else:
            return self.form_invalid(form)


class DistancePaceStatisticsView(BaseChangelistView):
    template_name = "for_runners/distance_pace_statistics.html"

    def get_context_data(self, **kwargs):
        qs = self.change_list.queryset  # get the filteres queryset form GpxModelChangeList
        qs = qs.order_by("length")
        context = {
            "tracks": qs,
            "track_count": qs.count(),
            "title": _("Distance/Pace Statistics"),
            "user": self.request.user,
            "opts": GpxModel._meta,
        }
        return context


class DistanceStatisticsView(BaseFormChangelistView):
    template_name = "for_runners/distance_statistics.html"
    form_class = DistanceStatisticsForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        form = context["form"]
        if form.is_valid():
            distance = form.cleaned_data["distance"]
        else:
            distance = INITIAL_DISTANCE

        distance_m = distance * 1000

        qs = self.change_list.queryset  # get the filteres queryset form GpxModelChangeList
        qs = qs.order_by("length")

        length_statistics = qs.aggregate(Min("length"), Avg("length"), Max("length"))

        min_length = length_statistics["length__min"]
        max_length = length_statistics["length__max"]

        current_distance_from = math.floor(min_length / 1000) * 1000
        current_distance_to = current_distance_from + distance_m

        group_data = collections.defaultdict(list)
        for track in qs:
            length = track.length
            # print("%.1fkm" % round(length/1000,1))
            if length > current_distance_to:
                while True:
                    current_distance_from += distance_m
                    current_distance_to += distance_m
                    if length > current_distance_to:
                        group_data[(current_distance_from, current_distance_to)] = []
                    else:
                        break

            group_data[(current_distance_from, current_distance_to)].append(track)

        print("group_data:")
        pprint(group_data)

        track_data = []
        total_tracks = 0
        for distances, tracks in sorted(group_data.items()):
            track_count = len(tracks)
            total_tracks += track_count
            distance_from, distance_to = distances

            if tracks:
                paces = [track.pace for track in tracks]
                min_paces = f"{min(paces):.2f}"
                avg_paces = f"{statistics.median(paces):.2f}"
                max_paces = f"{max(paces):.2f}"
            else:
                min_paces = "null"
                avg_paces = "null"
                max_paces = "null"

            track_data.append(
                (
                    round(distance_from / 1000, 1),
                    round(distance_to / 1000, 1),
                    track_count,
                    min_paces,
                    avg_paces,
                    max_paces,
                )
            )
        print("total track counts:", total_tracks)
        pprint(track_data)

        context.update(
            {
                "tracks": qs,
                "track_count": total_tracks,
                "min_length_km": round(min_length / 1000),
                "avg_length_km": round(length_statistics["length__avg"] / 1000),
                "max_length_km": round(max_length / 1000),
                "track_data": track_data,
                "title": _("Distance Statistics"),
                "user": self.request.user,
                "opts": GpxModel._meta,
            }
        )
        # pprint(context)
        return context


class GpxInfoView(BaseChangelistView):
    template_name = "for_runners/gpx_info.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "tracks": self.change_list.queryset,  # get the filteres queryset form GpxModelChangeList,
                "title": _("GPX Infomation"),
                "user": self.request.user,
                "opts": GpxModel._meta,
            }
        )
        return context


class GpxMetadataView(BaseChangelistView):
    template_name = "for_runners/gpx_metadata.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "tracks": self.change_list.queryset,  # get the filteres queryset form GpxModelChangeList
                "title": _("GPX Metadata"),
                "user": self.request.user,
                "opts": GpxModel._meta,
            }
        )
        return context


class PrintMiniView(generic.TemplateView):
    """
    Generate a page to print a small overview.
    """

    template_name = "admin/for_runners/gpxmodel/print_mini.html"

    def get(self, request):
        ids = request.GET["ids"].split(",")
        ids = [int(pk) for pk in ids]
        self.instances = GpxModel.objects.filter(pk__in=ids)
        return super().get(request)

    def get_context_data(self, **kwargs):
        gpx_tracks = []
        for gpx_track in self.instances:
            if not gpx_track.track_svg.name:
                log.critical("GPX Track has no svg file: %s", gpx_track)
                generate_svg(gpx_track, force=False)

            gpx_tracks.append(gpx_track)
        context = {"gpx_tracks": gpx_tracks, "back_url": reverse("admin:for_runners_gpxmodel_changelist")}
        return context


class CalculateValuesView(generic.View):
    def get(self, request, object_id):
        instance = GpxModel.objects.get(pk=object_id)
        instance.calculate_values()
        instance.save()
        messages.success(request, "Values are calculated from GPX data")
        return HttpResponseRedirect("../")


class StatisticsListFilter(admin.SimpleListFilter):
    title = _("statistics")
    template = "admin/for_runners/gpxmodel/filter.html"

    # Parameter for the filter that will be used in the URL query.
    parameter_name = constants.STATISTICS_PARAMETER_NAME

    def lookups(self, request, model_admin):
        return STATISTICS_CHOICES

    def queryset(self, request, queryset):
        return queryset


class GpxModelChangeList(ChangeList):
    def __init__(self, *args, **kwargs):
        self.startistics_mapping = {
            constants.DISPLAY_DISTANCE_PACE_KEY: DistanceStatisticsView,
            constants.DISPLAY_PACE_DURATION: DistancePaceStatisticsView,
            constants.DISPLAY_GPX_INFO: GpxInfoView,
            constants.DISPLAY_GPX_METADATA: GpxMetadataView,
        }

        # work-a-round for:
        #   __init__() missing 1 required positional argument: 'sortable_by'
        # while using export view
        # kwargs["sortable_by"] = None

        super().__init__(*args, **kwargs)

    def get_results(self, request):
        super().get_results(request)

        self.statistics = ""

        if constants.STATISTICS_PARAMETER_NAME in request.GET:
            if self.result_count == 0:
                log.debug("No tracks: no statistics.")
                return

            key = request.GET[constants.STATISTICS_PARAMETER_NAME]
            try:
                ViewClass = self.startistics_mapping[key]
            except KeyError as err:
                log.error("statistic view unknown: %s", err)
            else:
                view = ViewClass.as_view()
                response = view(request, self)
                assert isinstance(response, TemplateResponse), f"Method {view} didn't return a TemplateResponse!"
                self.statistics = response.rendered_content


class HasNetDurationFilter(admin.SimpleListFilter):
    title = _("has net duration")
    parameter_name = "net_duration"

    def lookups(self, request, model_admin):
        return (("y", _("yes")), ("n", _("no")))

    def queryset(self, request, queryset):
        if self.value() == "y":
            return queryset.exclude(participation__duration__isnull=True)
        if self.value() == "n":
            return queryset.filter(participation__duration__isnull=True)


class HasEventPartricipationFilter(admin.SimpleListFilter):
    title = _("has event participation")
    parameter_name = "participation"

    def lookups(self, request, model_admin):
        return (("y", _("yes")), ("n", _("no")))

    def queryset(self, request, queryset):
        if self.value() == "y":
            return queryset.exclude(participation__isnull=True)
        if self.value() == "n":
            return queryset.filter(participation__isnull=True)


@admin.register(GpxModel)
class GpxModelAdmin(ExportMixin, admin.ModelAdmin):
    actions = ["print_mini"]
    # change_list_template = 'admin/import_export/change_list_export.html'
    change_list_template = "admin/for_runners/gpxmodel/change_list.html"
    resource_class = GpxModelResource

    def print_mini(self, request, queryset):
        url = reverse("admin:print-mini")  # for_runners.admin.gpx.PrintMiniView
        selected = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
        return HttpResponseRedirect(f"{url}?ids={','.join(selected)}")

    print_mini.short_description = _("Generate a page to print a small overview.")

    def add_view(self, request, form_url="", extra_context=None):
        # redirect the defaul add view to upload form view:
        return HttpResponseRedirect(reverse("admin:upload-gpx-file"))

    @display_admin_error
    def leaflet_map_html(self, obj):
        gpxpy_instance = obj.get_gpxpy_instance()

        lat_list, lon_list = get_2d_coordinate_list(gpxpy_instance)
        coordinates = zip(lat_list, lon_list)

        km_gpx_points = iter_distance(gpxpy_instance, distance=1000)

        context = {
            "short_start_address": obj.short_start_address,
            "start_time": obj.start_time,
            "start_latitude": obj.start_latitude,
            "start_longitude": obj.start_longitude,
            "short_finish_address": obj.short_finish_address,
            "finish_time": obj.finish_time,
            "finish_latitude": obj.finish_latitude,
            "finish_longitude": obj.finish_longitude,
            "coordinates": coordinates,
            "km_gpx_points": km_gpx_points,
        }
        return render_to_string(template_name="admin/for_runners/gpxmodel/leaflet_map.html", context=context)

    leaflet_map_html.short_description = _("Route")

    @display_admin_error
    def dygraphs_html(self, obj):
        """
        Use dygraphs array format:
            http://dygraphs.com/data.html#array
        """
        gpxpy_instance = obj.get_gpxpy_instance()

        has_hr = None
        has_cad = None

        elevation_label = _("Elevation")

        labels = [_("Date"), elevation_label]
        columns = []

        time2coordinates = {}

        for point in iter_points(gpxpy_instance):
            add_extension_data(point)

            timestamp = point.time.timestamp() * 1000

            time2coordinates[timestamp] = (point.latitude, point.longitude)

            row = ["new Date(%i)" % timestamp, point.elevation]

            if has_hr is None or has_hr:
                try:
                    row.append(point.extension_data["hr"])
                except KeyError:
                    has_hr = False
                else:
                    if has_hr is None:
                        has_hr = True
                        labels.append(_("heart rate"))

            if has_cad is None or has_cad:
                try:
                    row.append(point.extension_data["cad"])
                except KeyError:
                    has_cad = False
                else:
                    if has_cad is None:
                        has_cad = True
                        labels.append(_("cadence"))

            columns.append(",".join([str(i) for i in row]))

        km_points = []
        for point, distance_m, distance_km in iter_distance(gpxpy_instance, distance=1000):
            km_points.append(
                {"x": "%i" % (point.time.timestamp() * 1000), "distance_m": distance_m, "distance_km": distance_km}
            )

        context = {
            "instance": obj,
            "labels": labels,
            "columns": columns,
            "elevation_label": elevation_label,
            "km_points": km_points,
            "time2coordinates": time2coordinates,
        }
        return render_to_string(template_name="admin/for_runners/gpxmodel/dygraphs.html", context=context)

    dygraphs_html.short_description = _("Graphs")

    def participation_links(self, obj):
        if not obj.participation:
            return "-"

        event = obj.participation.event
        gpx_tracks = GpxModel.objects.all().filter(participation__event=event).exclude(pk=obj.pk)

        context = {"event": event, "gpx_tracks": gpx_tracks}
        return render_to_string(template_name="admin/for_runners/gpxmodel/participation_links.html", context=context)

    participation_links.short_description = _("Links")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.list_display = [
            "tracked_by",
            "svg_tag",
            "overview",
            "start_time",
            "human_length_html",
            "human_duration_html",
            "human_pace",
            "heart_rate_avg",
            "human_weather",
            "uphill",
            "downhill",
            "min_elevation",
            "max_elevation",
        ]
        self.list_filter = [
            StatisticsListFilter,
            HasNetDurationFilter,
            HasEventPartricipationFilter,
            "tracked_by",
            "start_time",
            "ideal_distance",
            "creator",
        ]

    search_fields = ("full_start_address", "full_finish_address", "creator")
    date_hierarchy = "start_time"
    list_per_page = 50
    list_display_links = ("svg_tag", "overview")
    readonly_fields = (
        "leaflet_map_html",
        "dygraphs_html",
        "participation_links",
        "svg_tag_big",
        "svg_tag",
        "start_time",
        "start_latitude",
        "start_longitude",
        "finish_time",
        "finish_latitude",
        "finish_longitude",
        "start_coordinate_html",
        "finish_coordinate_html",
        "heart_rate_min",
        "heart_rate_avg",
        "heart_rate_max",
        "human_length_html",
        "human_duration_html",
        "human_pace",
    )

    fieldsets = (
        (_("Map / Graphs"), {"fields": ("leaflet_map_html", "dygraphs_html")}),
        (_("Event"), {"fields": ("participation", "participation_links")}),
        (
            _("Start"),
            {
                "fields": (
                    ("start_time", "start_temperature", "start_weather_state"),
                    "short_start_address",
                    "full_start_address",
                    "start_coordinate_html",
                    ("start_latitude", "start_longitude"),
                )
            },
        ),
        (
            _("Finish"),
            {
                "fields": (
                    ("finish_time", "finish_temperature", "finish_weather_state"),
                    "short_finish_address",
                    "full_finish_address",
                    "finish_coordinate_html",
                    ("finish_latitude", "finish_longitude"),
                )
            },
        ),
        (_("GPX data"), {"classes": ("collapse",), "fields": (("gpx", "points_no"), ("track_svg", "svg_tag_big"))}),
        (
            _("Values"),
            {
                "fields": (
                    ("human_length_html", "ideal_distance"),
                    ("human_duration_html", "human_pace"),
                    ("heart_rate_min", "heart_rate_avg", "heart_rate_max"),
                    ("uphill", "downhill"),
                    ("min_elevation", "max_elevation"),
                )
            },
        ),
    )
    # FIXME: Made this in CSS ;)
    formfield_overrides = {models.CharField: {"widget": forms.TextInput(attrs={"style": "width:70%"})}}

    def overview(self, obj):
        parts = []
        if obj.participation:
            event = obj.participation.event
            parts.append(f"<strong>{event}</strong>")
        parts.append(obj.start_end_address())
        html = "<br>".join(parts)
        return mark_safe(html)

    overview.short_description = _("Event")

    def get_urls(self):
        urls = super().get_urls()
        info = self.model._meta.app_label, self.model._meta.model_name
        urls = [
            url(r"^upload/$", self.admin_site.admin_view(UploadGpxFileView.as_view()), name="upload-gpx-file"),
            url(
                r"^distance-statistics/$",
                self.admin_site.admin_view(DistanceStatisticsView.as_view()),
                name="distance-statistics",
            ),
            url(
                r"^distance-pace-statistics/$",
                self.admin_site.admin_view(DistancePaceStatisticsView.as_view()),
                name="distance-pace-statistics",
            ),
            url(r"^print_mini/$", self.admin_site.admin_view(PrintMiniView.as_view()), name="print-mini"),
            url(
                r"^(.+)/calculate_values/$",
                self.admin_site.admin_view(CalculateValuesView.as_view()),
                name="%s_%s_calculate-values" % info,
            ),
        ] + urls
        return urls

    @cached_property
    def user_count(self):
        qs = GpxModel.objects.all().only("tracked_by").order_by("tracked_by")

        try:
            user_count = qs.distinct("tracked_by").count()
        except (NotImplementedError, NotSupportedError):
            # e.g.: sqlite has no distinct :(
            qs = qs.values_list("tracked_by__id", flat=True)
            user_count = len(set(qs))

        return user_count

    def get_list_display(self, request):
        list_display = super().get_list_display(request).copy()

        if self.user_count <= 1 and "tracked_by" in list_display:
            list_display.remove("tracked_by")

        return list_display

    def get_list_filter(self, request):
        list_filter = super().get_list_filter(request).copy()

        if self.user_count <= 1 and "tracked_by" in list_filter:
            list_filter.remove("tracked_by")

        return list_filter

    def get_changelist(self, request, **kwargs):
        """
        Returns the ChangeList class for use on the changelist page.
        """
        return GpxModelChangeList

    # def changelist_view(self, request, extra_context=None):
    #     if extra_context is None:
    #         extra_context = {}
    #

    #
    #     return super(GpxModelAdmin, self).changelist_view(request, extra_context)
