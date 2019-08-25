"""
    created 31.05.2018 by Jens Diemer <opensource@jensdiemer.de>
    :copyleft: 2018 by the django-for-runners team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import sys
from pathlib import Path

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

# https://github.com/jedie/django-for-runners
from for_runners.models import GpxModel
from for_runners.services.gpx_create import add_from_files


class Command(BaseCommand):
    help = "Import GPS files (*.gpx)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--username",
            "-u",
            action="store",
            dest="username",
            required=True,
            help="The user to assign to the imported files",
        )
        parser.add_argument("path", help="Path to *.gpx files")

    def handle(self, *args, **options):
        self.stdout.write("\n")
        self.stdout.write("_" * 79)
        self.stdout.write(self.help)
        self.stdout.write("\n")

        username = options.get("username")
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist as err:
            self.stderr.write("ERROR getting user %r: %s" % (username, err))
            user_names = ", ".join(User.objects.values_list("username", flat=True))
            self.stdout.write("Existing usernames are: %s" % user_names)
            sys.exit(3)

        self.stdout.write("Add new gpx tracks for user: %s" % user)

        path = Path(options.get("path"))
        path = path.expanduser()
        path = path.resolve()
        if not path.is_dir():
            self.stderr.write("ERROR: Given path '%s' is not a existing directory!" % path)
            sys.exit(4)

        self.stdout.write("Read directory: %s" % path)
        self.stdout.write("\n")

        new_tracks = 0
        for no, instance in enumerate(add_from_files(gpx_files_file_path=path, user=user), 1):
            self.stdout.write(self.style.SUCCESS("%i - Add new track: %s" % (no, instance)))
            new_tracks += 1

        self.stdout.write("\nimport done.\n")
        self.stdout.write(self.style.SUCCESS("Added %i new gpx tracks." % new_tracks))

        total_count = GpxModel.objects.filter(tracked_by=user).count()
        self.stdout.write("User %s has now %i tracks." % (user, total_count))
        self.stdout.write("\n")
