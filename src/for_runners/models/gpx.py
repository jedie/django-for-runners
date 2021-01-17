"""
    created 30.05.2018 by Jens Diemer <opensource@jensdiemer.de>
    :copyleft: 2018 by the django-for-runners team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import logging
from decimal import Decimal as D

from django.conf import settings
from django.db import models
from django.utils.safestring import mark_safe
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _
# https://github.com/jedie/django-tools
from django_tools.file_storage.file_system_storage import OverwriteFileSystemStorage
from django_tools.models import UpdateTimeBaseModel

# https://github.com/jedie/django-for-runners
from for_runners.gpx import GpxIdentifier, parse_gpx
from for_runners.gpx_tools.humanize import human_distance, human_duration, human_seconds
from for_runners.managers.gpx import GpxModelManager
from for_runners.model_utils import ModelAdminUrlMixin
from for_runners.models import DistanceModel, ParticipationModel


log = logging.getLogger(__name__)


def svg_upload_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return instance.get_svg_upload_path(filename=filename)


def gpx_upload_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return instance.get_gpx_upload_path(filename=filename)


class GpxModel(ModelAdminUrlMixin, UpdateTimeBaseModel):
    """
    inherit from ModelAdminUrlMixin:
        * get_admin_change_url()

    inherit from UpdateTimeBaseModel:
        * createtime
        * lastupdatetime
    """

    participation = models.OneToOneField(
        ParticipationModel, related_name="track", null=True, blank=True, on_delete=models.PROTECT
    )

    gpx = models.TextField(help_text="The raw gpx file content")
    gpx_file = models.FileField(
        verbose_name=_("GPX Track"),
        upload_to=gpx_upload_path,
        storage=OverwriteFileSystemStorage(create_backups=True),
        max_length=511,
        null=True,
        blank=True,
    )

    creator = models.CharField(help_text="Used device to create this track", max_length=511, null=True, blank=True)
    track_svg = models.FileField(
        verbose_name=_("Track SVG"),
        upload_to=svg_upload_path,
        storage=OverwriteFileSystemStorage(create_backups=False),
        null=True,
        blank=True,
    )

    start_time = models.DateTimeField(editable=False, help_text=_("Start time of the first segment in track"))
    start_latitude = models.FloatField(
        editable=False, help_text=_("Latitude of the first recorded point from the *.gpx file")
    )
    start_longitude = models.FloatField(
        editable=False, help_text=_("Longitude of the first recorded point from the *.gpx file")
    )
    start_temperature = models.FloatField(editable=True, null=True, blank=True, help_text=_("Temperature at start."))
    start_weather_state = models.CharField(max_length=127, null=True, blank=True, help_text="Weather state at start.")
    short_start_address = models.CharField(
        max_length=255, null=True, blank=True, help_text="The short address of the start point"
    )
    full_start_address = models.CharField(
        max_length=255, null=True, blank=True, help_text="The full address of the start point"
    )

    finish_time = models.DateTimeField(editable=False, help_text=_("End time of the last segment in track"))
    finish_latitude = models.FloatField(editable=False, help_text=_("Latitude of the finish point"))
    finish_longitude = models.FloatField(editable=False, help_text=_("Longitude of the finish point"))
    finish_temperature = models.FloatField(editable=True, null=True, blank=True, help_text=_("Temperature at finish."))
    finish_weather_state = models.CharField(
        max_length=127, null=True, blank=True, help_text="Weather state at finish."
    )
    short_finish_address = models.CharField(
        max_length=255, null=True, blank=True, help_text="The short address of the finish point"
    )
    full_finish_address = models.CharField(
        max_length=255, null=True, blank=True, help_text="The full address of the finish point"
    )

    tracked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        editable=False,
        related_name="%(class)s_createby",
        help_text="The user that tracked this gpx entry",
        on_delete=models.PROTECT,
    )
    lastupdateby = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        editable=False,
        related_name="%(class)s_lastupdateby",
        null=True,
        blank=True,
        help_text="User as last edit this entry",
        on_delete=models.SET_NULL,
    )

    points_no = models.PositiveIntegerField(help_text=_("Number of points in GPX"), null=True, blank=True)

    length = models.PositiveIntegerField(
        help_text=_(
            "Length in meters (calculated from GPX track 3-dimensional used latitude, longitude, and elevation)"
        ),
        null=True,
        blank=True,
    )
    ideal_distance = models.ForeignKey(
        to=DistanceModel,
        on_delete=models.SET_NULL,
        related_name="tracks",
        help_text=_("Length in meters (calculated 3-dimensional used latitude, longitude, and elevation)"),
        null=True,
        blank=True,
    )

    duration_s = models.PositiveIntegerField(
        help_text=_("Duration in seconds (from the GPX track)"), editable=False, null=True, blank=True
    )
    pace = models.DecimalField(
        help_text=_("Min/km (number of minutes it takes to cover a kilometer)"),
        max_digits=4,
        decimal_places=2,  # store numbers up to 99 with a resolution of 2 decimal places
        null=True,
        blank=True,
    )

    uphill = models.IntegerField(help_text=_("Uphill elevation climbs in meters"), null=True, blank=True)
    downhill = models.IntegerField(help_text=_("Downhill elevation descent in meters"), null=True, blank=True)

    min_elevation = models.IntegerField(help_text=_("Minimum elevation in meters"), null=True, blank=True)
    max_elevation = models.IntegerField(help_text=_("Maximum elevation in meters"), null=True, blank=True)

    heart_rate_min = models.PositiveIntegerField(
        help_text=_("Minimum heart rate."), null=True, blank=True, editable=False
    )
    heart_rate_avg = models.PositiveIntegerField(
        help_text=_("Average heart rate."), null=True, blank=True, editable=False
    )
    heart_rate_max = models.PositiveIntegerField(
        help_text=_("Maximum heart rate."), null=True, blank=True, editable=False
    )

    objects = GpxModelManager()

    def save(self, *args, **kwargs):

        if self.pace is not None:
            # avoid error like:
            # Ensure that there are no more than 2 decimal places.
            self.pace = D(self.pace).quantize(D("10.00"))

        self.full_clean()
        super().save(*args, **kwargs)

        # TODO: schedule request weather info, if not set

    def _get_track_upload_path(self, *, file_extension):
        """
        e.g:
            ~/DjangoForRunnersEnv/media/gpx_track_<date>/<prefix_id>.<file_extension>
        """
        date_prefix = self.start_time.strftime("%Y_%m")
        upload_path = "/".join(
            (
                # settings.MEDIA_ROOT,
                # TODO: Use https://github.com/jedie/django-tools/tree/master/django_tools/serve_media_app
                self.tracked_by.username,
                f"gpx_track_{date_prefix}",
                f"{self.get_prefix_id()}.{file_extension}",
            )
        )
        return upload_path

    def get_svg_upload_path(self, *, filename):
        """
        SVG file will be uploaded to e.g.:
        /home/<username>/DjangoForRunnersEnv/media/gpx_track_<date>/<prefix_id>.svg
        """
        svg_upload_path = self._get_track_upload_path(file_extension="svg")
        log.debug("Ignore source filename: %r upload to: %s", filename, svg_upload_path)
        return svg_upload_path

    def get_gpx_upload_path(self, *, filename):
        """
        GPX file will be uploaded to e.g.:
        /home/<username>/DjangoForRunnersEnv/media/gpx_track_<date>/<prefix_id>.gpx
        """
        gpx_upload_path = self._get_track_upload_path(file_extension="gpx")
        log.debug("Ignore source filename: %r upload to: %s", filename, gpx_upload_path)
        return gpx_upload_path

    def svg_tag(self):
        if self.track_svg:
            html = f'<img src="{self.track_svg.url}" alt="gpx track" height="70px" width="70px" />'
            return mark_safe(html)
        return ""

    svg_tag.short_description = _("SVG")

    def svg_tag_big(self):
        if self.track_svg:
            html = f'<img src="{self.track_svg.url}" alt="gpx track" height="200px" width="200px" />'
            return mark_safe(html)
        return ""

    svg_tag_big.short_description = _("SVG")

    def start_end_address(self):
        if self.short_start_address == self.short_finish_address:
            return f"⟳ {self.short_start_address}"
        html = f"{self.short_start_address}<br>▾<br>{self.short_finish_address}"
        return mark_safe(html)

    start_end_address.short_description = _("Start/End Address")

    def get_ideal_ratio(self):
        if self.ideal_distance:
            ratio = (float(self.ideal_distance.distance_km) * 1000) / self.length
            return ratio

    def get_ideal_duration_s(self):
        ratio = self.get_ideal_ratio()
        if ratio:
            return self.duration_s * ratio

    def get_ideal_pace(self):
        ratio = self.get_ideal_ratio()
        if ratio:
            return self.pace * ratio

    def get_ideal_distance_diff_m(self):
        if self.ideal_distance:
            distance_diff_m = (float(self.ideal_distance.distance_km) * 1000) - self.length
            return distance_diff_m

    def human_ideal_length(self):
        """
        used as labels in chart.js
        """
        if self.ideal_distance:
            return self.ideal_distance.get_human_distance()
        return human_distance(self.length / 1000)

    def human_length(self):
        if self.length:
            if self.ideal_distance:
                return self.ideal_distance.get_human_distance()
            else:
                return human_distance(self.length / 1000)

    def human_length_html(self):
        """
        Enhanced version of self.human_length()
        with more information via <span title="...">
        """
        if self.length:
            length_km = self.length / 1000

            if self.ideal_distance:
                diff_km = abs(self.get_ideal_distance_diff_m() / 1000)
                html = (
                    "<span"
                    ' title="{ideal} is the standardized distance'
                    ' - GPX-Track: {gpx} (diff: {diff})"'
                    ">{ideal}</span>"
                ).format(
                    ideal=self.ideal_distance.get_human_distance(),
                    gpx=human_distance(length_km),
                    diff=human_distance(diff_km),
                )
            else:
                html = ('<span title="real distance">%s</span>') % human_distance(length_km)

            return mark_safe(html)

    human_length_html.short_description = _("Length")
    human_length_html.admin_order_field = "length"

    def get_net_duration_s(self):
        if self.participation:
            # Use net duration from event participation
            return self.participation.get_duration_s()

    def human_duration(self):
        # Use net duration from event participation
        net_duration_s = self.get_net_duration_s()
        if net_duration_s is not None:
            return human_seconds(net_duration_s)

        ideal_duration_s = self.get_ideal_duration_s()
        if ideal_duration_s:
            return human_seconds(ideal_duration_s)

        if self.duration_s:
            return human_seconds(self.duration_s)

    def human_duration_html(self):
        """
        Enhanced version of self.human_duration()
        with more information via <span title="...">
        """
        net_duration_s = self.get_net_duration_s()
        if net_duration_s is not None:
            duration_diff = self.duration_s - net_duration_s
            html = (
                "<span"
                ' title="{net} is the official net duration'
                ' - GPX-Track: {gpx} (diff: {diff})"'
                ">{net}</span>"
            ).format(
                net=human_seconds(net_duration_s),
                gpx=human_seconds(self.duration_s),
                diff=human_duration(duration_diff),
            )
            return mark_safe(html)

        ideal_duration_s = self.get_ideal_duration_s()
        if ideal_duration_s:
            duration_diff = self.duration_s - ideal_duration_s
            html = (
                "<span"
                ' title="{ideal} is the standardized duration'
                ' - GPX-Track: {gpx} (diff: {diff})"'
                ">{ideal}</span>"
            ).format(
                ideal=human_seconds(ideal_duration_s),
                gpx=human_seconds(self.duration_s),
                diff=human_duration(duration_diff),
            )
            return mark_safe(html)

        if self.duration_s:
            html = ("<span" ' title="real duration"' ">%s</span>") % human_seconds(self.duration_s)
            return mark_safe(html)

    human_duration_html.short_description = _("Duration")
    human_duration_html.admin_order_field = "duration_s"

    def human_pace(self):
        if self.pace:
            return f"{human_seconds(self.pace * 60)} min/km"

    human_pace.short_description = _("Pace")
    human_pace.admin_order_field = "pace"

    def human_weather(self):
        if not self.start_temperature:
            return "-"
        html = f"{round(self.start_temperature, 1)}°C<br/>{self.start_weather_state}"
        return mark_safe(html)

    human_weather.short_description = _("Weather")
    human_weather.admin_order_field = "start_temperature"

    def _coordinate2link(self, lat, lon):
        html = (
            "<a"
            ' href="https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json&addressdetails=1"'
            ' title="Reverse {lat},{lon} address with OpenStreepMap"'
            ' target="_blank"'
            ">reverse address</a>"
            "<br>"
            "<a"
            ' href="https://www.openstreetmap.org/search?query={lat}%2C{lon}"'
            ' title="OpenStreepMap at {lat},{lon}"'
            ' target="_blank"'
            ">map</a>"
        ).format(lat=lat, lon=lon)
        return mark_safe(html)

    def start_coordinate_html(self):
        """
        return HTML Links for start point.
        """
        if self.start_latitude and self.start_longitude:
            return self._coordinate2link(lat=self.start_latitude, lon=self.start_longitude)

    start_coordinate_html.short_description = _("Start coordinates")

    def finish_coordinate_html(self):
        """
        return HTML Links for finish point.
        """
        if self.finish_latitude and self.finish_longitude:
            return self._coordinate2link(lat=self.finish_latitude, lon=self.finish_longitude)

    finish_coordinate_html.short_description = _("finish coordinates")

    def point_density(self):
        """
        Calculate the "density" of the GPX signal:
        :return: float - Meters/point count
        """
        if self.length > 0:
            density = self.length / self.points_no
            return density

    def gpx_meta(self):
        gpxpy_instance = self.get_gpxpy_instance()
        attr_names = (
            "version",
            "creator",
            "name",
            "description",
            "author_name",
            "author_email",
            "author_link",
            "author_link_text",
            "author_link_type",
            "copyright_author",
            "copyright_year",
            "copyright_license",
            "link",
            "link_text",
            "link_type",
            "time",
            "keywords",
        )
        result = []
        for attr_name in attr_names:
            value = getattr(gpxpy_instance, attr_name, None)
            if value:
                result.append((attr_name, value))

        return result

    _GPXPY_CACHE = {}

    def get_gpxpy_instance(self):
        try:
            return self._GPXPY_CACHE[self.pk]
        except KeyError:
            if self.gpx:
                gpxpy_instance = parse_gpx(content=self.gpx)
                if self.pk is not None:
                    self._GPXPY_CACHE[self.pk] = gpxpy_instance
                return gpxpy_instance

    def calc_pace(self):
        duration_s = self.get_net_duration_s()
        if not duration_s:
            duration_s = self.get_ideal_duration_s()
        if not duration_s:
            duration_s = self.duration_s
        if not duration_s:
            return None

        if self.ideal_distance:
            distance_km = int(self.ideal_distance.distance_km)
        else:
            distance_km = self.length / 1000

        try:
            pace = (duration_s / 60) / distance_km
        except ZeroDivisionError:
            # FIXME
            log.exception(f"Error calculate pace with duration {duration_s!r}sec and distance {distance_km}km!")
        else:
            if pace > 99 or pace < 0:
                log.error("Pace out of range: %f", pace)
            else:
                self.pace = pace

    def short_name(self, start_time=True):
        if self.pk is None:
            return "new, unsaved GPX Track"

        if start_time:
            parts = [self.start_time.strftime("%Y-%m-%d")]
        else:
            parts = []

        if self.participation:
            parts.append(self.participation.event.name)
        else:
            parts.append(self.short_start_address)
        result = " ".join([str(part) for part in parts if part])
        if result:
            return result
        return f"GPX Track ID:{self.pk}"

    def get_short_slug(self):
        name = self.short_name()
        return slugify(name)

    def get_prefix_id(self):
        gpxpy_instance = self.get_gpxpy_instance()
        prefix_id = GpxIdentifier(gpxpy_instance).get_prefix_id()
        return prefix_id

    def __str__(self):
        # return self.get_prefix_id()
        return self.short_name()

    class Meta:
        verbose_name = _("GPX Track")
        verbose_name_plural = _("GPX Tracks")
        unique_together = (
            ("start_time", "start_latitude", "start_longitude", "finish_time", "finish_latitude", "finish_longitude"),
        )
        ordering = ("-start_time", "-pk")
