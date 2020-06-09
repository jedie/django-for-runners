#!/usr/bin/env python3

import os
import sys
import traceback
from pathlib import Path
from threading import Timer

from django.contrib.auth import get_user_model
from django.contrib.staticfiles.management.commands.runserver import Command as RunServerCommand
from django.core.management import call_command

# https://github.com/jedie/django-for-runners
from for_runners.models import DistanceModel


DONT_OPEN_BROWSER_ENV_KEY = "DONT_OPEN_BROWSER"


class Command(RunServerCommand):
    """
    Expand django.contrib.staticfiles runserver
    """

    help = "Run Django-ForRunners with django developer server"

    def verbose_call(self, command, *args, **kwargs):
        self.stderr.write("_" * 79)
        self.stdout.write(f"Call {command!r} with: {args!r} {kwargs!r}")
        call_command(command, *args, **kwargs)

    def handle(self, *args, **options):

        if "RUN_MAIN" not in os.environ:
            # RUN_MAIN added by auto reloader, see: django/utils/autoreload.py

            # normally we can just do the following here::
            #   call_command("makemigrations")
            #   call_command("migrate")
            #
            # But this work until fix of: https://bitbucket.org/kbr/autotask/pull-requests/3/
            #
            # work-a-round: We call it in the shell script

            # django.contrib.staticfiles.management.commands.collectstatic.Command
            if sys.platform in ("win32", "cygwin"):
                # fix: CommandError: symbolic link privilege not held
                link = False
            else:
                link = True
            self.verbose_call("collectstatic", interactive=False, link=link)

            User = get_user_model()
            qs = User.objects.filter(is_active=True, is_superuser=True)
            if qs.count() == 0:
                self.verbose_call("createsuperuser")

            distance_model_count = DistanceModel.objects.all().count()
            if distance_model_count == 0:
                # call: for_runners.management.commands.fill_basedata.Command
                self.verbose_call("fill_basedata")

            if DONT_OPEN_BROWSER_ENV_KEY not in os.environ:

                def open_webbrowser():
                    os.environ[DONT_OPEN_BROWSER_ENV_KEY] = "yes"  # open only one time ;)

                    self.stderr.write("_" * 79)
                    self.stderr.write("Start web server...")

                    import webbrowser

                    addr = f"[{self.addr}]" if self._raw_ipv6 else self.addr
                    uri = f"{self.protocol}://{addr}:{self.port}/"
                    print(f"\nStart browser with: {uri!r}\n")
                    webbrowser.open_new_tab(uri)

                Timer(1, open_webbrowser).start()

        options["insecure_serving"] = True
        super().handle(*args, **options)

    def run(self, **options):

        if sys.platform in ("win32", "cygwin"):
            # Bugfix for:
            #   can't open file 'C:\Program Files\Django-ForRunners\Scripts\for_runners':
            #   [Errno 2] No such file or directory
            executable = Path(Path(sys.argv[0]).parent, "for_runners-script.py")
            print(f"Patch executeable to: {executable}")
            assert executable.is_file(), f"Executeable not found here: {executable}"
            sys.argv[0] = str(executable)

        try:
            super().run(**options)
        except Exception:
            traceback.print_last()
            raise
