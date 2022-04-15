"""
    created 30.05.2018 by Jens Diemer <opensource@jensdiemer.de>
    :copyleft: 2018 by the django-for-runners team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""
import datetime
import decimal
import math

from django.conf import settings
from django.utils.translation import ugettext_lazy as _


def human_seconds(duration):
    """
    >>> human_seconds(1)
    '0:01'
    >>> human_seconds(61)
    '1:01'
    >>> human_seconds(60*60+1)
    '1:00:01'
    """
    parts = []

    hours = None
    if duration > 1 * 60 * 60:
        hours = math.floor(duration / 60 / 60)
        duration -= hours * 60 * 60
        parts.append("%i" % hours)

    minutes = math.floor(duration / 60)
    if hours is None:
        parts.append("%i" % minutes)
    else:
        parts.append("%02i" % minutes)

    seconds = math.floor(duration - (minutes * 60))
    parts.append("%02i" % seconds)

    return ":".join(parts)


def human_duration(t):
    """
    Converts a time duration into a friendly text representation.

    >>> human_duration("type error")
    Traceback (most recent call last):
        ...
    decimal.InvalidOperation: [<class 'decimal.ConversionSyntax'>]


    >>> human_duration(datetime.timedelta(microseconds=1000))
    '1.0 ms'
    >>> human_duration(0.01)
    '10.0 ms'
    >>> human_duration(0.9)
    '900.0 ms'
    >>> human_duration(datetime.timedelta(seconds=1))
    '1.0 sec'
    >>> human_duration(65.5)
    '1.1 min'
    >>> human_duration(59.1 * 60)
    '59.1 min'
    >>> human_duration(60*60)
    '1.0 hours'
    >>> human_duration(1.06*60*60)
    '1.1 hours'
    >>> human_duration(datetime.timedelta(hours=24))
    '1.0 days'
    >>> human_duration(2.54 * 60 * 60 * 24 * 365)
    '2.5 years'
    """
    if isinstance(t, datetime.timedelta):
        t = decimal.Decimal(t.total_seconds())
    elif not isinstance(t, decimal.Decimal):
        t = decimal.Decimal(t)

    chunks = (
        (decimal.Decimal(60 * 60 * 24 * 365), _("years")),
        (decimal.Decimal(60 * 60 * 24 * 30), _("months")),
        (decimal.Decimal(60 * 60 * 24 * 7), _("weeks")),
        (decimal.Decimal(60 * 60 * 24), _("days")),
        (decimal.Decimal(60 * 60), _("hours")),
    )

    if t < 1:
        return _("%.1f ms") % round(t * 1000, 1)
    if t < 60:
        return _("%.1f sec") % round(t, 1)
    if t < 60 * 60:
        return _("%.1f min") % round(t / 60, 1)

    for seconds, name in chunks:
        count = t / seconds
        if count >= 1:
            count = round(count, 1)
            break
    return f"{count:.1f} {name}"


def human_distance(km):
    """
    >>> human_distance(km=0.10000001)
    '100 m'
    >>> human_distance(km=0.4)
    '400 m'
    >>> human_distance(km=0.0366) # 40 Yard Dash
    '36.6 m'
    >>> human_distance(km=10.0000)
    '10 km'
    >>> human_distance(km=21.0975)
    '21.0975 km'
    >>> human_distance(km=42.1950)
    '42.195 km'
    """
    if km < 1:
        m = round(km * 1000, 1)
        if m == int(m):
            return "%i m" % m
        return f"{m:.1f} m"

    if km == int(km):
        return f"{km:.0f} km"

    # FIXME:
    txt = f"{km:.4f}"
    txt = txt.rstrip("0")
    return f"{txt} km"


def convert_cash_values(value, round_value=True):
    """
    >>> convert_cash_values(10.60)
    '11 €'
    >>> convert_cash_values(10.60, round_value=False)
    '10.60 €'
    """
    if round_value:
        return "%i %s" % (round(value), settings.FOR_RUNNERS_CURRENCY_SYMBOL)
    else:
        return f"{value:.2f} {settings.FOR_RUNNERS_CURRENCY_SYMBOL}"
