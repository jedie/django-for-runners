"""
    Just print version line on every call from commandline ;)
"""
import os
import sys

from django import __version__ as django_version

from for_runners import __version__


if __name__ == 'for_runners_project':
    if '--version' not in sys.argv:
        print(f'Django-ForRunners v{__version__} (Django v{django_version})', file=sys.stderr)
        print(f'DJANGO_SETTINGS_MODULE={os.environ["DJANGO_SETTINGS_MODULE"]!r}', file=sys.stderr)
