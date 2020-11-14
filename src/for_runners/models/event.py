"""
    created 30.05.2018 by Jens Diemer <opensource@jensdiemer.de>
    :copyleft: 2018 by the django-for-runners team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import logging
from urllib.parse import urlparse

from django.conf import settings
from django.db import models
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django_tools.models import UpdateInfoBaseModel, UpdateTimeBaseModel

from for_runners.gpx_tools.humanize import human_distance, human_seconds
from for_runners.model_utils import ModelAdminUrlMixin
from for_runners.models import DisciplineModel


log = logging.getLogger(__name__)


def human_url(url):
    scheme, netloc, url, params, query, fragment = urlparse(url)
    text = netloc + url
    text = text.strip("/")
    if text.startswith("www."):
        text = text[4:]
    return text


class LinkModelBase(UpdateTimeBaseModel):
    """
    inherit and automatically set from UpdateTimeBaseModel:
     * createtime
     * lastupdatetime
    """

    url = models.URLField(help_text=_("Link URL"))
    text = models.CharField(
        max_length=127, help_text=_("Link text (leave empty to generate it from url)"), null=True, blank=True
    )
    title = models.CharField(
        max_length=127, help_text=_("Link title (leave empty to generate it from url)"), null=True, blank=True
    )

    def get_text(self):
        return self.text or human_url(self.url)

    def get_title(self):
        return self.title or self.url

    def link_html(self):
        html = ('<a href="{url}" title="{title}" target="_blank">' "{text}" "</a>").format(
            url=self.url, title=self.get_title(), text=self.get_text()
        )
        return mark_safe(html)

    link_html.short_description = _("Link")

    def save(self, *args, **kwargs):
        if self.text is None:
            self.text = human_url(self.url)

        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.get_text()

    class Meta:
        abstract = True


class EventModel(ModelAdminUrlMixin, UpdateInfoBaseModel):
    """
    inherit from ModelAdminUrlMixin:
        * get_admin_change_url()

    inherit from UpdateInfoBaseModel:
        * createtime
        * lastupdatetime
        * createby
        * lastupdateby
    """

    no = models.PositiveIntegerField(help_text=_("Sequential number of the event"), null=True, blank=True)
    name = models.CharField(max_length=255, help_text=_("Name of the event"))
    start_date = models.DateField(help_text=_("Start date of the run"), null=True, blank=True)
    discipline = models.ForeignKey(DisciplineModel, on_delete=models.SET_NULL, null=True)

    def short_name(self):
        parts = []
        if self.no:
            parts.append("%i." % self.no)
        parts.append(self.name)
        result = " ".join([part for part in parts if part])
        return result

    def verbose_name(self):
        parts = [self.short_name()]
        if self.start_date:
            year = self.start_date.strftime("%Y")
            if year not in self.name:
                parts.append(year)
        result = " ".join([part for part in parts if part])
        return result

    verbose_name.short_description = _("Event Name")
    verbose_name.admin_order_field = "name"

    def links_html(self):
        links = []
        for link in self.links.all():
            links.append(link.link_html())
        html = "<br />".join(links)
        return mark_safe(html)

    links_html.short_description = _("Links")

    def __str__(self):
        return self.verbose_name()

    class Meta:
        verbose_name = _("Event")
        verbose_name_plural = _("Events")
        ordering = ("-start_date", "-pk")


class EventLinkModel(LinkModelBase):
    event = models.ForeignKey(EventModel, related_name="links", on_delete=models.CASCADE)


class ParticipationModel(ModelAdminUrlMixin, UpdateTimeBaseModel):
    """
    inherit from ModelAdminUrlMixin:
        * get_admin_change_url()

    inherit from UpdateTimeBaseModel:
        * createtime
        * lastupdatetime
    """

    event = models.ForeignKey(EventModel, related_name="participations", on_delete=models.CASCADE)
    person = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="+",
        help_text="The person who participated to this competition.",
        on_delete=models.CASCADE,
    )
    distance_km = models.DecimalField(
        help_text=_("Official track length in kilometer."),
        # store numbers up to 999 with a resolution of 4 decimal places
        max_digits=7,
        decimal_places=4,
    )
    duration = models.TimeField(
        verbose_name=_("Duration"), help_text=_("You officially measured finisher time"), null=True, blank=True
    )
    start_number = models.CharField(max_length=15, help_text=_("Your start number"), null=True, blank=True)
    finisher_count = models.PositiveIntegerField(
        help_text=_("Number of participants who have finished in your discipline"), null=True, blank=True
    )

    def get_human_distance(self):
        return human_distance(self.distance_km)

    get_human_distance.short_description = _("Distance")
    get_human_distance.admin_order_field = "distance_km"

    def get_duration_s(self):
        """
        :return: duration in seconds
        """
        if self.duration:
            # FIXME: Is there really no easier way to do this?
            duration = self.duration.second
            duration += self.duration.minute * 60
            duration += self.duration.hour * 60 * 60
            return duration

    def human_duration(self):
        if self.duration:
            return human_seconds(self.get_duration_s())

    def get_pace_s(self):
        if self.duration:
            pace = (self.get_duration_s() / 60) / float(self.distance_km)
            if pace > 99 or pace < 0:
                log.error("Pace out of range: %f", pace)
            else:
                return pace * 60

    def verbose_name(self):
        parts = [self.event.verbose_name(), "-", self.person.username, "-", self.get_human_distance()]
        if self.duration:
            parts.append(f"in {self.human_duration()}")

        result = " ".join([part for part in parts if part])
        return result

    verbose_name.short_description = _("Event Name")
    verbose_name.admin_order_field = "name"

    def __str__(self):
        return self.verbose_name()

    class Meta:
        verbose_name = _("Event Participation")
        verbose_name_plural = _("Event Participations")
        ordering = ("-event__start_date", "person")


class CostModel(UpdateTimeBaseModel):
    """
    inherit and automatically set from UpdateTimeBaseModel:
     * createtime
     * lastupdatetime
    """

    participation = models.ForeignKey(ParticipationModel, related_name="costs", on_delete=models.CASCADE)
    name = models.CharField(max_length=15, help_text=_("The name of the item you dis pay for"))
    amount = models.DecimalField(
        help_text=_("How much did you pay for this?"),
        max_digits=8,
        decimal_places=2,  # store numbers up to 99 with a resolution of 2 decimal places
    )

    def __str__(self):
        return f"{self.name}: {self.amount}"

    class Meta:
        verbose_name = _("Participation Cost")
        verbose_name_plural = _("Participation Costs")
