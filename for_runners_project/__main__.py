"""
    Helper to call django manage commands
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    used in
    for, e.g.:

    ~/DjangoForRunnersEnv/bin/python3 -m for_runners_project --help
"""
import os
import sys

from django.core.management import execute_from_command_line


def manage():
    os.environ["DJANGO_SETTINGS_MODULE"] = "for_runners_project.settings"
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    manage()
