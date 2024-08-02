import io

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

        out = io.StringIO()
        call_command(FillBasedataCommand(), stdout=out)

        distances = sorted(DistanceModel.objects.values_list('distance_km', flat=True))
        self.assertEqual(distances, sorted(settings.BASE_IDEAL_TRACK_LENGTHS))

        output = out.getvalue()
        self.assertIn('Create: <DistanceModel: 21.0975 km>', output)
        self.assertIn('Create: <DistanceModel: 42.195 km>', output)

        # Run again will not change anything:
        out = io.StringIO()
        call_command(FillBasedataCommand(), stdout=out)

        self.assertEqual(sorted(DistanceModel.objects.values_list('distance_km', flat=True)), distances)

        output = out.getvalue()
        self.assertIn('<DistanceModel: 21.0975 km> already exists, ok.', output)
        self.assertIn('<DistanceModel: 42.195 km> already exists, ok.', output)
        self.assertIn('No track updated needed, ok.', output)
