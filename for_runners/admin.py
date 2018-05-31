"""
    created 30.05.2018 by Jens Diemer <opensource@jensdiemer.de>
    :copyleft: 2018 by the django-for-runners team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""
import io
import logging

from django import forms
from django.conf.urls import url
from django.contrib import admin, messages
from django.db import models
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
from django.views import generic

# https://github.com/jedie/django-for-runners
from for_runners.forms import UploadGpxFileForm
from for_runners.gpx_tools.garmin2gpxpy import garmin2gpxpy
from for_runners.gpx_tools.gpxpy2map import generate_map
from for_runners.models import DisciplineModel, EventModel, GpxModel

log = logging.getLogger(__name__)


@admin.register(DisciplineModel)
class DisciplineModelAdmin(admin.ModelAdmin):
    pass


@admin.register(EventModel)
class EventModelAdmin(admin.ModelAdmin):
    pass


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
                if f.content_type != "application/gpx+xml":
                    messages.error(request, "Ignore %r file %r!" % (f.content_type, f.name))
                    continue
                messages.info(request, "Process %s..." % f.name)

                content = f.file.read()
                log.debug("raw content......: %s", repr(content)[:100])
                content = content.decode("utf-8")
                log.debug("decoded content..: %s", repr(content)[:100])

                gpx = GpxModel.objects.create(gpx=content)
                gpx.calculate_values()
                messages.success(request, "Created: %s" % gpx)

            return self.form_valid(form)
        else:
            return self.form_invalid(form)


class ProcessGpxDataView(generic.View):

    def get(self, request, object_id):
        instance = GpxModel.objects.get(pk=object_id)
        log.debug("Process GPX %s" % instance)

        content = instance.gpx
        gpxpy_instance = garmin2gpxpy(content)

        image, plt = generate_map(gpxpy_instance)

        temp = io.BytesIO()
        plt.savefig(temp, bbox_inches="tight")

        # Save gpx map file to model instance:
        instance.map_image.save("gpx", temp)

        messages.success(request, "GPX data saved to %s, ok." % instance)
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
    list_display = (
        # "image_tag",
        "svg_tag",
        "event",
        "short_start_address",
        "start_time",
        "human_length",
        "human_duration",
        "human_pace",
        "uphill",
        "downhill",
        "min_elevation",
        "max_elevation",
        "tracked_by"
    )
    list_display_links = (
        "event",
        "short_start_address",
    )
    readonly_fields = (
        "svg_tag_big",
        "image_tag",
        "svg_tag",
        "start_time",
        "start_latitude",
        "start_longitude",
        "finish_time",
        "finish_latitude",
        "finish_longitude",
        "start_coordinate_html",
    )

    fieldsets = (
        (_("Event"), {
            "fields": (
                "event",
                ("track_svg", "svg_tag_big"),
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
                ("finish_latitude", "finish_longitude"),
            )
        }),
        (_("GPX data"), {
            "classes": ("collapse",),
            "fields": (
                ("gpx", "points_no"),
            )
        }),
        (_("Values"), {
            "fields": (
                ("length", "duration", "pace"),
                ("uphill", "downhill"),
                ("min_elevation", "max_elevation"),
            )
        }),
    )
    # FIXME: Made this in CSS ;)
    formfield_overrides = {models.CharField: {'widget': forms.TextInput(attrs={'style': 'width:70%'})}}

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
