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
        
         File "...Django-ForRunners/src/django-for-runners/for_runners/management/commands/import_gpx.py", line 70, in handle
            self.stdout.write(self.style.SUCCESS("%i - Add new track: %s" % (no, instance)))
          File "...Django-ForRunners/lib/python3.6/site-packages/django/core/management/base.py", line 145, in write
            self._out.write(style_func(msg))
        UnicodeEncodeError: 'ascii' codec can't encode character '\xdf' in position 42: ordinal not in range(128)
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
            self.stderr.write("UnicodeEncodeError: %s" % err)
            self.stderr.write("\n")
            self.stderr.write("Hint:")
            self.stderr.write(" - Maybe python output encoding falls back to ASCII ?")
            self.stderr.write(" - setup your locales or set LANG or PYTHONIOENCODING ;)")
            self.stderr.write("\n")
            self.stderr.write("locale: %s" % repr(locale.getlocale()))
            self.stderr.write("LANG: %r" % os.environ.get("LANG"))
            self.stderr.write("PYTHONIOENCODING: %r" % os.environ.get("PYTHONIOENCODING"))
            self.stderr.write("sys.stdout.encoding: %r" % sys.stdout.encoding)
            self.stderr.write("\n")
            self.stderr.write("*" * 79)
            self.stderr.write("\n")
            raise
