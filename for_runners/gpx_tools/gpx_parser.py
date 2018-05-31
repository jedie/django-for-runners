"""
    created 31.05.2018 by Jens Diemer <opensource@jensdiemer.de>
    :copyleft: 2018 by the django-for-runners team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""
import io
from pathlib import Path

import gpxpy

from for_runners.gpx_tools.garmin2gpxpy import garmin2gpxpy





def parse_gpx_file(filepath):
    assert isinstance(filepath, Path)
    assert filepath.is_file()

    with filepath.open("r") as f:
        content = f.read()

    return parse_gpx(content)
