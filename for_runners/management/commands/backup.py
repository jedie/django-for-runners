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
from for_runners_project.utils.venv import VirtualEnvPath

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

            user_csv_path = Path(backup_path, "runnings_%s.csv" % user.username)
            with user_csv_path.open("w", encoding='utf-8', newline='') as f:
                user_csv_writer = csv.writer(f)

                qs = gpx_user_tracks(user=user)
                total_count = qs.count()
                for no, track in enumerate(qs):
                    print("\t [%i/%i] track: %s" % (no, total_count, track))

                    filename = "%s.gpx" % track.get_short_slug()

                    file_path = Path(out_path, filename)
                    with file_path.open("w") as f:
                        f.write(track.gpx)

                    user_csv_writer.writerow([
                        track.short_name(), track.tracked_by.username,
                        round(track.length / 1000, 2)
                    ])

    def csv_export(self, *, backup_path):
        csv_path = Path(backup_path, "runnings.csv")

        HEADER_DATE = "date"
        HEADER_NAME = "name"
        HEADER_EVENT = "event"
        HEADER_USER = "user"
        HEADER_LENGTH = "length (km)"
        HEADER_DURATION = "duration"
        HEADER_PACE = "pace"
        HEADER_HEART_RATE = "heart rate"
        HEADER_TEMPERATURE = "temperature"
        HEADER_WEATHER = "weather"
        HEADER_CREATOR = "creator"

        with csv_path.open("w", encoding='utf-8', newline='') as csv_file:
            fieldnames = [
                HEADER_DATE,
                HEADER_NAME,
                HEADER_EVENT,
                HEADER_USER,
                HEADER_LENGTH,
                HEADER_DURATION,
                HEADER_PACE,
                HEADER_HEART_RATE,
                HEADER_TEMPERATURE,
                HEADER_WEATHER,
                HEADER_CREATOR,
            ]
            csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            csv_writer.writeheader()

            qs = gpx_tracks(has_gpx=True)
            total_count = qs.count()
            for no, track in enumerate(qs):
                print("\t [%i/%i] track: %s" % (no, total_count, track))

                if track.heart_rate_avg:
                    heart_rate = "%i b/m" % track.heart_rate_avg
                else:
                    heart_rate = ""

                if track.start_temperature:
                    temperature = "%i°C" % round(track.start_temperature, 1)
                    weather = track.start_weather_state
                else:
                    temperature = ""
                    weather = ""

                csv_writer.writerow({
                    HEADER_DATE: track.start_time.isoformat(),
                    HEADER_NAME: track.short_name(start_time=False),
                    HEADER_EVENT: "x" if track.participation else "",
                    HEADER_USER: track.tracked_by.username,
                    HEADER_LENGTH: round(track.length / 1000, 2),
                    HEADER_DURATION: track.human_duration(),
                    HEADER_PACE: track.human_pace(),
                    HEADER_HEART_RATE: heart_rate,
                    HEADER_TEMPERATURE: temperature,
                    HEADER_WEATHER: weather,
                    HEADER_CREATOR: track.creator,
                })

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

        self.csv_export(backup_path=backup_path)

        # TODO: Save svg

        print("\n*** Backup completed.")
