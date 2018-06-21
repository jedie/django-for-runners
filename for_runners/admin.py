"""
    created 30.05.2018 by Jens Diemer <opensource@jensdiemer.de>
    :copyleft: 2018 by the django-for-runners team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""
import io
import logging

from autotask.tasks import delayed_task
from django import forms
from django.conf.urls import url
from django.contrib import admin, messages
from django.db import IntegrityError, models
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
from django.views import generic
# https://github.com/jedie/django-for-runners
from for_runners.exceptions import GpxDataError
from for_runners.forms import UploadGpxFileForm
from for_runners.gpx_tools.garmin2gpxpy import garmin2gpxpy
from for_runners.gpx_tools.gpxpy2map import generate_map
from for_runners.models import (DisciplineModel, EventLinkModel, EventModel, GpxModel)

log = logging.getLogger(__name__)


@admin.register(DisciplineModel)
class DisciplineModelAdmin(admin.ModelAdmin):
    pass


@admin.register(EventLinkModel)
class EventLinkModelAdmin(admin.ModelAdmin):
    pass


class LinkModelInline(admin.TabularInline):
    model = EventLinkModel
    extra = 2
    min_num = 1
    max_num = None
    fields = (
        'url',
        'text',
        'title',
    )


@admin.register(EventModel)
class EventModelAdmin(admin.ModelAdmin):
    list_display = ("verbose_name", "links_html", "start_time", "discipline")
    list_display_links = ("verbose_name",)
    inlines = [
        LinkModelInline,
    ]


class UploadGpxFileView(generic.FormView):
    template_name = "for_runners/upload_gpx_file.html"
    form_class = UploadGpxFileForm
    success_url = "../"  # FIXME

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        files = request.FILES.getlist("gpx_files")
        if form.is_valid():
            log.debug("files: %r", files)
            for f in files:
                messages.info(request, "Process %s..." % f.name)

                content = f.file.read()
                log.debug("raw content......: %s", repr(content)[:100])
                content = content.decode("utf-8")
                log.debug("decoded content..: %s", repr(content)[:100])

                try:
                    try:
                        gpx = GpxModel.objects.create(gpx=content)
                    except IntegrityError as err:
                        messages.error(request, "Error process GPX data: %s" % err)
                        continue

                    gpx.calculate_values()
                except GpxDataError as err:
                    messages.error(request, "Error process GPX data: %s" % err)
                else:
                    messages.success(request, "Created: %s" % gpx)

            return self.form_valid(form)
        else:
            return self.form_invalid(form)


class ProcessGpxDataView(generic.View):

    def get(self, request, object_id):
        """
        Create delayed task to generate the map of the GPX Track
        """
        messages.info(request, "GPX Map will be generated in background")

        gpx_instance = GpxModel.objects.get(pk=object_id)
        gpx_instance.schedule_generate_map()

        return HttpResponseRedirect("../")


class CalculateValuesView(generic.View):

    def get(self, request, object_id):
        instance = GpxModel.objects.get(pk=object_id)
        instance.calculate_values()
        instance.save()
        messages.success(request, "Values are calculated from GPX data")
        return HttpResponseRedirect("../")


@admin.register(GpxModel)
class GpxModelAdmin(admin.ModelAdmin):
    search_fields = (
        "full_start_address",
        "full_finish_address",
    )
    list_display = (
        "svg_tag",
        "overview", "start_time", "human_length", "human_duration", "human_pace", "heart_rate_avg",
        "uphill", "downhill", "min_elevation", "max_elevation", "tracked_by"
    )
    list_filter = (
        "tracked_by",
    )
    list_display_links = (
        "svg_tag",
        "overview",
    )
    readonly_fields = (
        "leaflet_map_html",
        "chartjs_html",
        "svg_tag_big", "image_tag", "svg_tag", "start_time", "start_latitude", "start_longitude", "finish_time",
        "finish_latitude", "finish_longitude",
        "start_coordinate_html", "finish_coordinate_html",
        "heart_rate_min", "heart_rate_avg", "heart_rate_max"
    )

    fieldsets = (
        (_("Event"), {
            "fields": (
                "event",
                "leaflet_map_html",
                "chartjs_html",
                ("map_image", "image_tag"),
            )
        }),
        (_("Start"), {
            "fields": (
                "start_time",
                "short_start_address",
                "full_start_address",
                "start_coordinate_html",
                ("start_latitude", "start_longitude"),
            )
        }),
        (_("Finish"), {
            "fields": (
                "finish_time",
                "short_finish_address",
                "full_finish_address",
                "finish_coordinate_html",
                ("finish_latitude", "finish_longitude"),
            )
        }),
        (_("GPX data"), {
            "classes": ("collapse",),
            "fields": (
                ("gpx", "points_no"),
                ("track_svg", "svg_tag_big"),
            )
        }),
        (_("Values"), {
            "fields": (
                ("length", "duration", "pace"),
                ("heart_rate_min","heart_rate_avg","heart_rate_max"),
                ("uphill", "downhill"),
                ("min_elevation", "max_elevation"),
            )
        }),
    )
    # FIXME: Made this in CSS ;)
    formfield_overrides = {models.CharField: {'widget': forms.TextInput(attrs={'style': 'width:70%'})}}

    def overview(self, obj):
        parts = []
        if obj.event:
            parts.append("<strong>%s</strong>" % obj.event)
        parts.append(obj.start_end_address())
        html = "<br>".join(parts)
        return html

    overview.short_description = _("Event")
    overview.allow_tags = True

    def get_urls(self):
        urls = super().get_urls()
        info = self.model._meta.app_label, self.model._meta.model_name
        urls = [
            url(r"^upload/$", self.admin_site.admin_view(UploadGpxFileView.as_view()), name="upload-gpx-file"),
            url(
                r"^(.+)/process/$",
                self.admin_site.admin_view(ProcessGpxDataView.as_view()),
                name="%s_%s_process-gpx-data" % info
            ),
            url(
                r"^(.+)/calculate_values/$",
                self.admin_site.admin_view(CalculateValuesView.as_view()),
                name="%s_%s_calculate-values" % info
            ),
        ] + urls
        return urls
