"""
    created 30.05.2018 by Jens Diemer <opensource@jensdiemer.de>
    :copyleft: 2018 by the django-for-runners team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""
import decimal
import math
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
    if duration>1*60*60:
        hours = math.floor(duration/60/60)
        duration -= hours*60*60
        parts.append("%i" % hours)

    minutes = math.floor(duration/60)
    if hours is None:
        parts.append("%i" % minutes)
    else:
        parts.append("%02i" % minutes)

    seconds = math.floor(duration - (minutes*60))
    parts.append("%02i" % seconds)

    return ":".join(parts)


def human_duration(t):
    """
    Converts a time duration into a friendly text representation.

    >>> human_duration("type error")
    Traceback (most recent call last):
        ...
    TypeError: human_duration() argument must be timedelta, integer or float)


    >>> human_duration(datetime.timedelta(microseconds=1000))
    u'1.0 ms'
    >>> human_duration(0.01)
    u'10.0 ms'
    >>> human_duration(0.9)
    u'900.0 ms'
    >>> human_duration(datetime.timedelta(seconds=1))
    u'1.0 sec'
    >>> human_duration(65.5)
    u'1.1 min'
    >>> human_duration((60 * 60)-1)
    u'59.0 min'
    >>> human_duration(60*60)
    u'1.0 hours'
    >>> human_duration(1.05*60*60)
    u'1.1 hours'
    >>> human_duration(datetime.timedelta(hours=24))
    u'1.0 days'
    >>> human_duration(2.54 * 60 * 60 * 24 * 365)
    u'2.5 years'
    """
    assert isinstance(t, decimal.Decimal)

    chunks = (
      (decimal.Decimal(60 * 60 * 24 * 365), _('years')),
      (decimal.Decimal(60 * 60 * 24 * 30), _('months')),
      (decimal.Decimal(60 * 60 * 24 * 7), _('weeks')),
      (decimal.Decimal(60 * 60 * 24), _('days')),
      (decimal.Decimal(60 * 60), _('hours')),
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
    return "%(number).1f %(type)s" % {'number': count, 'type': name}


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
        return "%.1f m" % m

    if km == int(km):
        return "%.0f km" % km

    # FIXME:
    txt = "%.4f" % km
    txt = txt.rstrip("0")
    return "%s km" % txt