"""
    created 30.05.2018 by Jens Diemer <opensource@jensdiemer.de>
    :copyleft: 2018 by the django-for-runners team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import logging

from django.db import models
from django.utils.translation import ugettext_lazy as _


log = logging.getLogger(__name__)


class DisciplineModel(models.Model):
    name = models.CharField(max_length=255, help_text=_("Sport discipline"))

    def __str__(self):
        return self.name
