#!/usr/bin/env python3

import os

from django.contrib.auth import get_user_model
from django.contrib.staticfiles.management.commands.runserver import Command as RunServerCommand
from django.core.management import call_command

# https://github.com/jedie/django-for-runners
from for_runners.models import DistanceModel


class Command(RunServerCommand):
    """
    Expand django.contrib.staticfiles runserver
    """
    help = "Setup test project and run django developer server"

    def verbose_call(self, command, *args, **kwargs):
        self.stderr.write("_" * 79)
        self.stdout.write("Call %r with: %r %r" % (command, args, kwargs))
        call_command(command, *args, **kwargs)

    def handle(self, *args, **options):

        if "RUN_MAIN" not in os.environ:
            # RUN_MAIN added by auto reloader, see: django/utils/autoreload.py
            self.verbose_call("makemigrations")  # helpfull for developming and add/change models ;)
            self.verbose_call("migrate")

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
