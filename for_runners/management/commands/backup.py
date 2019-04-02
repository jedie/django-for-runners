"""
    created 17.11.2018 by Jens Diemer <opensource@jensdiemer.de>
    :copyleft: 2018 by the django-for-runners team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""
import csv
import datetime
import logging
import shutil
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.text import slugify

# https://github.com/jedie/django-for-runners
from for_runners.selectors.gpx import gpx_tracks, gpx_user_tracks, gpx_users
from for_runners.services.gpx_svg_generator import CsvGenerator
from for_runners_project.utils.venv import VirtualEnvPath

log = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    TODO: Use for_runners.admin.gpx_import_export.GpxModelResource
    """

    help = "Backup everything"

    def backup_database(self, *, backup_path):
        db_file = Path(settings.DATABASES["default"]["NAME"])
        if not db_file.is_file():
            print("Error database file not found: %s" % db_file)
        else:
            db_file_bak = Path(backup_path, db_file.name)
            print("Backup database file to: %s" % db_file_bak)
            shutil.copyfile(str(db_file), str(db_file_bak))

    def csv_user_export(self, *, backup_path):
        """
        Export all .gpx tracks
            * create sub directory from username
            * generate .csv file per user
        """
        for user in gpx_users():
            print("Export for user: %s" % user.username)

            out_path = Path(backup_path, user.username)
            out_path.mkdir(parents=True, exist_ok=False)

            user_csv_path = Path(backup_path, "runnings_%s.csv" % user.username)

            tracks = 0

            with user_csv_path.open("w", encoding="utf-8", newline="") as csv_file:
                csv_generator = CsvGenerator(csv_file=csv_file, add_username=False)

                for track in gpx_user_tracks(user=user):
                    print(".", end="", flush=True)

                    filename = "%s.gpx" % track.get_short_slug()

                    file_path = Path(out_path, filename)
                    with file_path.open("w") as f:
                        f.write(track.gpx)

                    # output one csv row:
                    csv_generator.add_gpx_track(track=track)

                    tracks += 1

            print("\n%i trackes saved for user: %s\n" % (tracks, user.username))

    def csv_complete_export(self, *, backup_path):

        csv_path = Path(backup_path, "runnings.csv")
        print("Generate %s..." % csv_path)

        tracks = 0

        with csv_path.open("w", encoding="utf-8", newline="") as csv_file:
            csv_generator = CsvGenerator(csv_file=csv_file, add_username=True)

            for track in gpx_tracks(has_gpx=True):
                print(".", end="", flush=True)

                # output one csv row:
                csv_generator.add_gpx_track(track=track)

                tracks += 1

        print("\n%i trackes\n" % tracks)

    def handle(self, *args, **options):

        venv_path = VirtualEnvPath()
        env_path = venv_path.env_path
        print("virtualenv path: %s" % env_path)

        now = datetime.datetime.now()
        timestamp = now.strftime("%Y%m%d_%H%M")

        backup_path = Path(env_path, "backups", timestamp)

        print("_" * 100)
        print(" *** Create backup to: %s ***" % backup_path)
        print()

        backup_path.mkdir(parents=True, exist_ok=False)

        # Backup SQLite database file:
        self.backup_database(backup_path=backup_path)

        # Export gpx tracks and create user-csv-file:
        self.csv_user_export(backup_path=backup_path)

        # Generate .csv file for all tracks:
        self.csv_complete_export(backup_path=backup_path)

        # TODO: Save svg

        print("\n*** Backup completed.")
