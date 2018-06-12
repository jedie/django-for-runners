"""
    created 30.05.2018 by Jens Diemer <opensource@jensdiemer.de>
    :copyleft: 2018 by the django-for-runners team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import math


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
