import math

from django.db import models
from django.utils.translation import ugettext_lazy as _

from for_runners.gpx_tools.garmin2gpxpy import garmin2gpxpy

# https://github.com/jedie/django-tools
from django_tools.models import UpdateInfoBaseModel
from for_runners.gpx_tools.humanize import human_seconds


class DisciplineModel(models.Model):
    name = models.CharField(max_length=255, help_text=_("Sport discipline."))

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
        help_text=_("Sequential number of the event."),
        null=True, blank=True,
    )
    name = models.CharField(max_length=255, help_text=_("Name of the event."))
    start_time = models.DateTimeField(help_text=_("Start date/time of the run."),
        null=True, blank=True,
    )
    discipline = models.ForeignKey(DisciplineModel)

    def __str__(self):
        return "%i. %s %s" % (self.no, self.name, self.start_time)


class GpxModel(UpdateInfoBaseModel):
    """
    inherit from UpdateInfoBaseModel:
        * createtime
        * lastupdatetime
        * createby
        * lastupdateby
    """
    event = models.ForeignKey(
        EventModel,
        null=True,
        blank=True,
    )

    gpx = models.TextField(help_text="The raw gpx file content",)
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

    start_time = models.DateTimeField(
        help_text=_("Start time of the first segment in track"),
        null=True, blank=True,
    )
    end_time = models.DateTimeField(
        help_text=_("End time of the last segment in track"),
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
            return "%s min/km" % human_seconds(self.pace*60)
    human_pace.short_description = _("Pace")

    def get_gpxpy_instance(self):
        gpxpy_instance = garmin2gpxpy(content=self.gpx)
        return gpxpy_instance

    def calculate_values(self):
        gpxpy_instance = self.get_gpxpy_instance()
        self.points_no = gpxpy_instance.get_points_no()
        self.length = gpxpy_instance.length_3d()
        self.duration = gpxpy_instance.get_duration()
        self.pace = (self.duration/60) / (self.length/1000)

        time_bounds = gpxpy_instance.get_time_bounds()
        self.start_time = time_bounds.start_time
        self.end_time = time_bounds.end_time



        uphill_downhill = gpxpy_instance.get_uphill_downhill()
        self.uphill = uphill_downhill.uphill
        self.downhill = uphill_downhill.downhill

        elevation_extremes = gpxpy_instance.get_elevation_extremes()
        self.min_elevation = elevation_extremes.minimum
        self.max_elevation = elevation_extremes.maximum

        self.save()

    def __str__(self):
        if self.event:
            return "%s" % self.event
        if self.start_time:
            return "%s" % self.start_time
        return "GPX Track ID:%s" % self.pk

    class Meta:
        verbose_name = _('GPX Track')
        verbose_name_plural = _('GPX Tracks')
        ordering = ('-start_time', '-pk')
