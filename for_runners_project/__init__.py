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

    if 'DJANGO_SETTINGS_MODULE' not in os.environ:
        if 'test' in sys.argv or 'coverage' in sys.argv or 'tox' in sys.argv:
            DJANGO_SETTINGS_MODULE = 'for_runners_project.settings.tests'
        else:
            DJANGO_SETTINGS_MODULE = 'for_runners_project.settings.local'

        print(f'Set {DJANGO_SETTINGS_MODULE=}', file=sys.stderr)
        os.environ['DJANGO_SETTINGS_MODULE'] = DJANGO_SETTINGS_MODULE
    else:
        print(f'DJANGO_SETTINGS_MODULE={os.environ["DJANGO_SETTINGS_MODULE"]}', file=sys.stderr)
