"""
    created 30.05.2018 by Jens Diemer <opensource@jensdiemer.de>
    :copyleft: 2018 by the django-for-runners team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import logging

from django.db import models
from django.utils.translation import ugettext_lazy as _

# https://github.com/jedie/django-for-runners
from for_runners.gpx_tools.humanize import human_distance


log = logging.getLogger(__name__)


class DistanceModel(models.Model):
    distance_km = models.DecimalField(
        help_text=_("The ideal track length in kilometer."),
        unique=True,
        # store numbers up to 999 with a resolution of 4 decimal places
        max_digits=7,
        decimal_places=4,
    )
    variance = models.PositiveSmallIntegerField(
        help_text=_("Maximum (+/-) deviation in percent to match this distance."), default=5
    )
    min_distance_m = models.PositiveIntegerField(editable=False, blank=True, null=True)
    max_distance_m = models.PositiveIntegerField(editable=False, blank=True, null=True)

    def _set_min_max(self):
        distance_m = self.distance_km * 1000
        variance_m = self.get_variance_m()
        self.min_distance_m = round(distance_m - variance_m)
        self.max_distance_m = round(distance_m + variance_m)

    def save(self, *args, **kwargs):
        self._set_min_max()
        log.debug("Save: %s", self)
        self.full_clean()
        super().save(*args, **kwargs)

    def get_variance_m(self):
        variance_km = self.distance_km / 100 * self.variance
        return variance_km * 1000

    def get_human_distance(self):
        return human_distance(self.distance_km)

    get_human_distance.short_description = _("Distance")
    get_human_distance.admin_order_field = "distance_km"

    def get_human_variance(self):
        return "%i %%" % self.variance

    get_human_variance.short_description = _("Variance")

    def get_human_variance_as_length(self):
        return human_distance(self.get_variance_m() / 1000)

    get_human_variance_as_length.short_description = _("Variance")

    def get_human_min_max(self):
        return f"{human_distance(self.min_distance_m / 1000)} - {human_distance(self.max_distance_m / 1000)}"

    get_human_min_max.short_description = _("Min/Max")

    def __str__(self):
        return self.get_human_distance()

    class Meta:
        verbose_name = _("Distance")
        verbose_name_plural = _("Distances")
        ordering = ("-distance_km",)
