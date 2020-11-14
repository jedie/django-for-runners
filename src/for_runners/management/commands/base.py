"""
    created 25.08.2019 by Jens Diemer <opensource@jensdiemer.de>
    :copyleft: 2018 by the django-for-runners team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import locale
import os
import sys

from django.core.management import BaseCommand as DjangoBaseCommand


class BaseCommand(DjangoBaseCommand):
    def execute(self, *args, **kwargs):
        """
        Just display a hint on UnicodeEncodeError

        e.g.:
        terminal encoding fallback to ASCII (e.g.: wrong server config in a ssh session)
        call gpx import command and the track contains non ASCII characters

         File ".../for_runners/management/commands/import_gpx.py", line 70, in handle
            self.stdout.write(self.style.SUCCESS("%i - Add new track: %s" % (no, instance)))
          File ".../python3.6/site-packages/django/core/management/base.py", line 145, in write
            self._out.write(style_func(msg))
        UnicodeEncodeError: 'ascii' codec can't encode character '\xdf' in position 42:...
        """
        self.stdout.write("\n")
        self.stdout.write("_" * 79)
        self.stdout.write(self.help)
        self.stdout.write("\n")

        try:
            return super().execute(*args, **kwargs)
        except UnicodeEncodeError as err:

            self.stderr.write("\n")
            self.stderr.write("*" * 79)
            self.stderr.write(f"UnicodeEncodeError: {err}")
            self.stderr.write("\n")
            self.stderr.write("Hint:")
            self.stderr.write(" - Maybe python output encoding falls back to ASCII ?")
            self.stderr.write(" - setup your locales or set LANG or PYTHONIOENCODING ;)")
            self.stderr.write("\n")
            self.stderr.write(f"locale: {repr(locale.getlocale())}")
            self.stderr.write(f"LANG: {os.environ.get('LANG')!r}")
            self.stderr.write(f"PYTHONIOENCODING: {os.environ.get('PYTHONIOENCODING')!r}")
            self.stderr.write(f"sys.stdout.encoding: {sys.stdout.encoding!r}")
            self.stderr.write("\n")
            self.stderr.write("*" * 79)
            self.stderr.write("\n")
            raise
