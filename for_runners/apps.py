"""
    https://docs.djangoproject.com/en/2.0/ref/applications/#configuring-applications-ref

    created 04.07.2018 by Jens Diemer <opensource@jensdiemer.de>
    :copyleft: 2018 by the django-for-runners team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""
from pathlib import Path

from django.apps import AppConfig
from django.conf import settings


class ForRunnersConfig(AppConfig):
    name = 'for_runners'
    verbose_name = "ForRunners"

    def ready(self):
        base_path = Path(settings.FOR_RUNNERS_DATA_FILE_PATH)
        if base_path.is_dir():
            print("Use existing base path: %s" % base_path)
        else:
            print("Create base path: %s..." % base_path, end=" ")
            base_path.mkdir(mode=0o777, parents=True, exist_ok=False)
            print("OK")
