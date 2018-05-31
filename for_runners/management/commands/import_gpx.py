"""
    created 31.05.2018 by Jens Diemer <opensource@jensdiemer.de>
    :copyleft: 2018 by the django-for-runners team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""
import sys
from pathlib import Path

from django.core.management.base import BaseCommand
from django.db import IntegrityError

from cms.models import User

# https://github.com/jedie/django-for-runners
from for_runners.models import GpxModel


class Command(BaseCommand):
    help = "Import GPS files (*.gpx)"

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            "-u",
            action='store',
            dest='username',
            required=True,
            help="The user to assign to the imported files"
        )
        parser.add_argument("path", help="Path to *.gpx files")

    def handle(self, *args, **options):
        username = options.get("username")
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist as err:
            print("ERROR getting user %r: %s" % username, err)
            sys.exit(-1)

        path = Path(options.get("path"))
        if not path.is_dir():
            print("ERROR: Given path '%s' is not a existing directory!" % path)
            sys.exit(-1)

        gpx_files = path.glob('**/*.gpx')
        for gpx_file in gpx_files:
            with gpx_file.open("r") as f:
                gpx_content = f.read()

            try:
                instance = GpxModel.objects.add_gpx(gpx_content, user)
            except IntegrityError as err:
                print("Skip .gpx file: %s" % err)
            else:
                print(instance)
