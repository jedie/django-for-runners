"""
    created 12.06.2018 by Jens Diemer <opensource@jensdiemer.de>
    :copyleft: 2018 by the django-for-runners team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import io
import logging

import autocron

from for_runners.gpx_tools.garmin2gpxpy import garmin2gpxpy


log = logging.getLogger(__name__)


@autocron.delay
def generate_gpx_map_task(object_id):
    """
    Delayed task to generate the map from GPX track
    """
    log.debug("Generate GPX Map for ID: %r", object_id)

    from for_runners.models import GpxModel  # import here, because of import-loop

    gpx_instance = GpxModel.objects.get(pk=object_id)
    log.info(f"Generate GPX Map for: {gpx_instance}")

    content = gpx_instance.gpx
    gpxpy_instance = garmin2gpxpy(content)

    image, plt = generate_map(gpxpy_instance)

    temp = io.BytesIO()
    plt.savefig(temp, bbox_inches="tight")

    filename = f"{gpx_instance.get_short_slug()}.png"

    # Save gpx map file to model instance:
    gpx_instance.map_image.save(filename, temp)

    log.info(f"GPX data saved to {gpx_instance}, ok.")
