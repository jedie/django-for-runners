"""
    created 17.11.2018 by Jens Diemer <opensource@jensdiemer.de>
    :copyleft: 2018 by the django-for-runners team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""
import datetime
import logging
import shutil
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.text import slugify

from for_runners_project.utils.venv import VirtualEnvPath

# https://github.com/jedie/django-for-runners
from for_runners.selectors.gpx import gpx_user_tracks, gpx_users

log = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Backup everything"

    def backup_database(self, *, backup_path):
        db_file = Path(settings.DATABASES["default"]["NAME"])
        if not db_file.is_file():
            print("Error database file not found: %s" % db_file)
        else:
            db_file_bak = Path(backup_path, db_file.name)
            print("Backup database file to: %s" % db_file_bak)
            shutil.copyfile(str(db_file), str(db_file_bak))

    def backup_gpx_tracks(self, *, backup_path):
        for user in gpx_users():
            print("User: %s" % user.username)
            out_path = Path(backup_path, user.username)
            out_path.mkdir(parents=True, exist_ok=False)

            qs = gpx_user_tracks(user=user)
            total_count = qs.count()
            for no, track in enumerate(qs):
                print("\t [%i/%i] track: %s" % (no, total_count, track))

                filename = "%s.gpx" % track.get_short_slug()

                file_path = Path(out_path, filename)
                with file_path.open("w") as f:
                    f.write(track.gpx)


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

        self.backup_database(backup_path=backup_path)

        self.backup_gpx_tracks(backup_path=backup_path)

        # TODO: Save svg
        # TODO: Save events

        print("\n*** Backup completed.")
