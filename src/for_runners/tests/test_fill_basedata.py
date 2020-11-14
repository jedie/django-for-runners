from django.conf import settings
from django.core.management import call_command
from django.test import TestCase

# https://github.com/jedie/django-for-runners
from for_runners.management.commands.fill_basedata import Command as FillBasedataCommand
from for_runners.models import DistanceModel


class FillBasedataCommandTestCase(TestCase):
    def test_import_no_username_given(self):
        assert len(settings.BASE_IDEAL_TRACK_LENGTHS) > 0
        assert DistanceModel.objects.count() == 0

        call_command(FillBasedataCommand())

        assert DistanceModel.objects.count() == len(settings.BASE_IDEAL_TRACK_LENGTHS)
