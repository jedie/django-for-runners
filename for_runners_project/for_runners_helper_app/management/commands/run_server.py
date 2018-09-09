#!/usr/bin/env python3

import os
from threading import Timer

from django.contrib.auth import get_user_model
from django.contrib.staticfiles.management.commands.runserver import Command as RunServerCommand
from django.core.management import call_command

# https://github.com/jedie/django-for-runners
from for_runners.models import DistanceModel


class Command(RunServerCommand):
    """
    Expand django.contrib.staticfiles runserver
    """
    help = "Run Django-ForRunners with django developer server"

    def verbose_call(self, command, *args, **kwargs):
        self.stderr.write("_" * 79)
        self.stdout.write("Call %r with: %r %r" % (command, args, kwargs))
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
            self.verbose_call("collectstatic", interactive=False, link=True)

            User = get_user_model()
            qs = User.objects.filter(is_active=True, is_superuser=True)
            if qs.count() == 0:
                self.verbose_call("createsuperuser")

            distance_model_count = DistanceModel.objects.all().count()
            if distance_model_count == 0:
                # call: for_runners.management.commands.fill_basedata.Command
                self.verbose_call("fill_basedata")

        options["insecure_serving"] = True
        super(Command, self).handle(*args, **options)

    def run(self, **options):

        if "RUN_MAIN" in os.environ and not "DONT_OPEN_BROWSER" in os.environ:
            # Just open browser and point to the server URI
            # But only one time ;)
            # "DONT_OPEN_BROWSER" set in for_runners_project.cli.run_dev_server
            def open_webbrowser():
                import webbrowser
                uri = "%(protocol)s://%(addr)s:%(port)s/" % {
                    "protocol": self.protocol,
                    "addr": '[%s]' % self.addr if self._raw_ipv6 else self.addr,
                    "port": self.port,
                }
                print("\nStart browser with: %r\n" % uri)
                webbrowser.open_new_tab(uri)

            Timer(1, open_webbrowser).start()

        super().run(**options)