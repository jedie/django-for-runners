"""
    created 30.05.2018 by Jens Diemer <opensource@jensdiemer.de>
    :copyleft: 2018 by the django-for-runners team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import math


def human_seconds(duration):
    minutes = math.floor(duration/60)
    seconds = math.floor(duration - (minutes*60))
    return "%i:%02i" % (minutes, seconds)
