"""
    Django-ForRunners App settings
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    include in your own settings.py e.g.:

        from for_runners.app_settings import *

    created 28.06.2018 by Jens Diemer <opensource@jensdiemer.de>
    :copyleft: 2018 by the django-for-runners team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import decimal


# Base data for:
#   for_runners.models.distance.DistanceModel
#
# Can be change via:
#   settings.BASE_IDEAL_TRACK_LENGTHS
#
# Used in
#   for_runners.management.commands.fill_basedata.Command
#
BASE_IDEAL_TRACK_LENGTHS = (  # All values are in kilometers ;)
    decimal.Decimal('0.4'),
    decimal.Decimal('0.8'),
    decimal.Decimal('5.0'),
    decimal.Decimal('6.5'),
    decimal.Decimal('7.5'),
    decimal.Decimal('8.5'),
    decimal.Decimal('10.0'),
    decimal.Decimal('21.0975'),
    decimal.Decimal('42.195'),
)

# All cash values are stored as decimal field without any currency information
# This symbol will be just added ;)
FOR_RUNNERS_CURRENCY_SYMBOL = "€"
