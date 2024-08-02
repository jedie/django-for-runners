"""
    created 28.06.2018 by Jens Diemer <opensource@jensdiemer.de>
    :copyleft: 2018 by the django-for-runners team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


from django.conf import settings

# https://github.com/jedie/django-for-runners
from for_runners.management.commands.base import BaseCommand
from for_runners.models import DistanceModel, GpxModel


class Command(BaseCommand):
    help = "Create some base data"

    def handle(self, *args, **options):
        updated_needed = False
        for distance_km in settings.BASE_IDEAL_TRACK_LENGTHS:
            obj, created = DistanceModel.objects.get_or_create(distance_km=distance_km)
            if created:
                updated_needed = True
                self.stdout.write(f"Create: {repr(obj)}")
            else:
                obj.full_clean()
                self.stdout.write(f"{repr(obj)} already exists, ok.")

        if not updated_needed:
            self.stdout.write("No track updated needed, ok.")
        else:
            print("Update existing tracks", end="")
            for track in GpxModel.objects.all():
                track.save()
                print(".", end="", flush=True)
            self.stdout.write('done.')
