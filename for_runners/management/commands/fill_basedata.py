"""
    created 28.06.2018 by Jens Diemer <opensource@jensdiemer.de>
    :copyleft: 2018 by the django-for-runners team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from django.conf import settings
from django.core.management.base import BaseCommand
from for_runners.models import DistanceModel, GpxModel


class Command(BaseCommand):
    help = "Create some base data"

    def handle(self, *args, **options):

        updated_needed = False

        for distance_km in settings.BASE_IDEAL_TRACK_LENGTHS:
            obj, created = DistanceModel.objects.get_or_create(
                distance_km=distance_km)
            if created:
                updated_needed = True
                self.stdout.write("Create: %s" % repr(obj))
            else:
                self.stdout.write("%s already exists, ok." % repr(obj))

        if not updated_needed:
            print("No track updated needed, ok.")
        else:
            for track in GpxModel.objects.all():
                track.save()
                print(".", end="", flush=True)
            print()
