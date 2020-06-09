"""
    created 17.11.2018 by Jens Diemer <opensource@jensdiemer.de>
    :copyleft: 2018-2019 by the django-for-runners team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""
import logging

# https://github.com/jedie/django-for-runners
from for_runners.management.commands.base import BaseCommand
from for_runners.models import GpxModel
from for_runners.services.gpx_save_gpx import save_gpx_file
from for_runners.services.gpx_svg_generator import generate_svg


log = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    call this e.g.:

        ~/Django-ForRunners/bin$ ./manage recreate_files
    """

    help = "Recreate all svg, gpx files for existing gpx tracks on disk"

    def handle(self, *args, **options):
        qs = GpxModel.objects.all()
        total_count = qs.count()
        for no, gpx_track in enumerate(qs):
            print("[%i/%i] Generate for: %s" % (no, total_count, gpx_track))

            if not gpx_track.gpx:
                continue

            generate_svg(gpx_track=gpx_track, force=True)
            save_gpx_file(gpx_track=gpx_track, force=True)

            gpx_track.save()
