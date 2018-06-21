"""
    created 12.06.2018 by Jens Diemer <opensource@jensdiemer.de>
    :copyleft: 2018 by the django-for-runners team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from pathlib import Path

from django.test import TestCase
from django_tools.unittest_utils.user import TestUserMixin
# https://github.com/jedie/django-for-runners
from for_runners.models import GpxModel

BASE_PATH = Path(__file__).parent


class GpxTests(TestUserMixin, TestCase):

    def test_parse_gpx(self):

        user = self._get_user(usertype="normal")

        filepath = Path(BASE_PATH, "fixture_files/garmin_connect_1.gpx")
        with filepath.open("r") as f:
            gpx_content = f.read()

        instance = GpxModel.objects.add_gpx(gpx_content, user)
        print(instance)

        self.assertEqual(repr(instance), "<GpxModel: 2018-02-21 Moers Hülsdonk>")

        self.assertEqual(instance.points_no, 3)
        self.assertEqual(round(instance.length, 3), 4.718)
        self.assertEqual(instance.duration, 2)
        self.assertEqual(round(instance.pace, 3), 7.065)
        self.assertEqual(instance.heart_rate_avg, 125)

        self.assertEqual(instance.get_short_slug(), "2018-02-21-moers-hulsdonk")