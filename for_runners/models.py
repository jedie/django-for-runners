"""
    created 30.05.2018 by Jens Diemer <opensource@jensdiemer.de>
    :copyleft: 2018 by the django-for-runners team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""
import io
import logging

from django.conf import settings
from django.core.files import File
from django.db import models
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from filer.fields.file import FilerFileField
from filer.utils.loader import load_model

# https://github.com/jedie/django-tools
from django_tools.models import UpdateInfoBaseModel, UpdateTimeBaseModel

# https://github.com/jedie/django-for-runners
from for_runners.geo import reverse_geo
from for_runners.gpx import get_identifier, parse_gpx
from for_runners.gpx_tools.humanize import human_seconds
from for_runners.managers import GpxModelManager
from for_runners.svg import gpx2svg_string

log = logging.getLogger(__name__)


class DisciplineModel(models.Model):
    name = models.CharField(max_length=255, help_text=_("Sport discipline"))

    def __str__(self):
        return self.name


class EventModel(UpdateInfoBaseModel):
    """
    inherit from UpdateInfoBaseModel:
        * createtime
        * lastupdatetime
        * createby
        * lastupdateby
    """
    no = models.IntegerField(
        help_text=_("Sequential number of the event"),
        null=True, blank=True,
    )
    name = models.CharField(max_length=255, help_text=_("Name of the event"))
    start_time = models.DateTimeField(help_text=_("Start date/time of the run"),
        null=True, blank=True,
    )
    discipline = models.ForeignKey(DisciplineModel)

    def __str__(self):
        return "%i. %s %s" % (self.no, self.name, self.start_time)


class GpxModel(UpdateTimeBaseModel):
    """
    inherit from UpdateTimeBaseModel:
        * createtime
        * lastupdatetime
    """
    event = models.ForeignKey(
        EventModel,
        null=True,
        blank=True,
    )

    gpx = models.TextField(help_text="The raw gpx file content",)
    track_svg = FilerFileField(verbose_name=_("Track SVG"), related_name="+",
        null=True,
        blank=True,
    )

    start_time = models.DateTimeField(editable=False,
        help_text=_("Start time of the first segment in track"),
    )
    start_latitude = models.FloatField(editable=False,
        help_text=_("Latitude of the first recorded point from the *.gpx file"),
    )
    start_longitude = models.FloatField(editable=False,
        help_text=_("Longitude of the first recorded point from the *.gpx file"),
    )
    short_start_address = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="The short address of the start point",
    )
    full_start_address = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="The full address of the start point",
    )

    finish_time = models.DateTimeField(editable=False,
        help_text=_("End time of the last segment in track"),
    )
    finish_latitude = models.FloatField(editable=False,
        help_text=_("Latitude of the finish point"),
    )
    finish_longitude = models.FloatField(editable=False,
        help_text=_("Longitude of the finish point"),
    )
    short_finish_address = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="The short address of the finish point",
    )
    full_finish_address = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="The full address of the finish point",
    )

    tracked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        editable=False,
        related_name="%(class)s_createby",
        null=True,
        blank=True,
        help_text="The user that tracked this gpx entry",
        on_delete=models.SET_NULL
    )
    lastupdateby = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        editable=False,
        related_name="%(class)s_lastupdateby",
        null=True,
        blank=True,
        help_text="User as last edit this entry",
        on_delete=models.SET_NULL
    )



    points_no = models.PositiveIntegerField(
        help_text=_("Number of points in GPX"),
        null=True, blank=True,
    )

    length = models.PositiveIntegerField(
        help_text=_("Length in meters (calculated 3-dimensional used latitude, longitude, and elevation)"),
        null=True, blank=True,
    )
    duration = models.PositiveIntegerField(
        help_text=_("Duration in seconds"),
        null=True, blank=True,
    )
    pace = models.DecimalField(
        help_text=_("Min/km (number of minutes it takes to cover a kilometer)"),
        max_digits=4, decimal_places=2, # store numbers up to 99 with a resolution of 2 decimal places
        null=True, blank=True,
    )

    uphill = models.IntegerField(
        help_text=_("Uphill elevation climbs in meters"),
        null=True, blank=True,
    )
    downhill = models.IntegerField(
        help_text=_("Downhill elevation descent in meters"),
        null=True, blank=True,
    )
    min_elevation = models.IntegerField(
        help_text=_("Minimum elevation in meters"),
        null=True, blank=True,
    )
    max_elevation = models.IntegerField(
        help_text=_("Maximum elevation in meters"),
        null=True, blank=True,
    )

    map_image = models.ImageField(
        null=True,
        blank=True,
    )

    objects = GpxModelManager()

    def save(self, *args, **kwargs):
        if self.gpx:
            self.calculate_values()

        super().save(*args, **kwargs)

    def svg_tag(self):
        if self.track_svg:
            return '<img src="{}" alt="gpx track" height="70px" width="70px" />'.format(self.track_svg.url)
        return ""

    svg_tag.short_description = _("SVG")
    svg_tag.allow_tags = True

    def svg_tag_big(self):
        if self.track_svg:
            return '<img src="{}" alt="gpx track" height="200px" width="200px" />'.format(self.track_svg.url)
        return ""

    svg_tag_big.short_description = _("SVG")
    svg_tag_big.allow_tags = True

    def image_tag(self):
        if self.map_image:
            return '<img src="%s" />' % self.map_image.url
        return ""

    image_tag.short_description = _("Map Image")
    image_tag.allow_tags = True

    def human_length(self):
        if self.length:
            kilometers = self.length / 1000
            return "%.2f km" % kilometers
    human_length.short_description = _("Length")

    def human_duration(self):
        if self.duration:
            return human_seconds(self.duration)
    human_duration.short_description = _("Duration")

    def human_pace(self):
        if self.pace:
            return "%s min/km" % human_seconds(self.pace * 60)
    human_pace.short_description = _("Pace")

    def _coordinate2link(self, lat, lon):
        return (
            '<a'
            ' href="https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json&addressdetails=1"'
            ' target="_blank"'
            '>'
            '{lat},{lon}'
            '</a>'
        ).format(
            lat=lat, lon=lon
        )

    def start_coordinate_html(self):
        """
        https://nominatim.openstreetmap.org/reverse?lat=51.20638179592788&lon=6.803598012775183&format=json&addressdetails=1
        """
        return self._coordinate2link(
            lat=self.start_latitude,
            lon=self.start_longitude,
        )

    start_coordinate_html.short_description = _("Start coordinates")
    start_coordinate_html.allow_tags = True

    def get_gpxpy_instance(self):
        gpxpy_instance = parse_gpx(content=self.gpx)
        return gpxpy_instance

    def calculate_values(self):
        gpxpy_instance = self.get_gpxpy_instance()
        self.points_no = gpxpy_instance.get_points_no()
        self.length = gpxpy_instance.length_3d()
        self.duration = gpxpy_instance.get_duration()
        self.pace = (self.duration / 60) / (self.length / 1000)

        uphill_downhill = gpxpy_instance.get_uphill_downhill()
        self.uphill = uphill_downhill.uphill
        self.downhill = uphill_downhill.downhill

        elevation_extremes = gpxpy_instance.get_elevation_extremes()
        self.min_elevation = elevation_extremes.minimum
        self.max_elevation = elevation_extremes.maximum

        identifier = get_identifier(gpxpy_instance)
        self.start_time = identifier.start_time
        self.finish_time = identifier.finish_time
        self.start_latitude = identifier.start_lat
        self.start_longitude = identifier.start_lon
        self.finish_latitude = identifier.finish_lat
        self.finish_longitude = identifier.finish_lon

        try:
            start_address = reverse_geo(self.start_latitude, self.start_longitude)
        except Exception as err:
            # e.g.: geopy.exc.GeocoderTimedOut: Service timed out
            log.error("Can't reverse geo: %s" % err)
        else:
            self.short_start_address = start_address.short
            self.full_start_address = start_address.full

        try:
            finish_address = reverse_geo(self.finish_latitude, self.finish_longitude)
        except Exception as err:
            # e.g.: geopy.exc.GeocoderTimedOut: Service timed out
            log.error("Can't reverse geo: %s" % err)
        else:
            self.short_finish_address = finish_address.short
            self.full_finish_address = finish_address.full

        # if not self.track_svg:
        log.debug("Create SVG from GPX...")
        svg_string = gpx2svg_string(gpxpy_instance)

        # import filer.models.imagemodels.Image
        Image = load_model(settings.FILER_IMAGE_MODEL)

        temp = io.BytesIO(bytes(svg_string, "utf-8"))
        django_file_obj = File(temp, name="gpx.svg")
        filer_image = Image.objects.create(
            owner=self.tracked_by, original_filename="gpx.svg", file=django_file_obj, folder=None
        )
        filer_image.save()

        # self.track_svg.save("gpx2svg", svg_string)
        self.track_svg = filer_image  #save("gpx2svg", svg_string)

    def __str__(self):
        parts = [self.start_time, self.event, self.short_start_address]
        result = " ".join([str(part) for part in parts if part])
        if result:
            return result
        return "GPX Track ID:%s" % self.pk

    class Meta:
        verbose_name = _('GPX Track')
        verbose_name_plural = _('GPX Tracks')
        unique_together = ((
            "start_time", "start_latitude", "start_longitude", "finish_time", "finish_latitude", "finish_longitude"
        ),)
        ordering = ('-start_time', '-pk')
