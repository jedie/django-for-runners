"""
    created 12.06.2018 by Jens Diemer <opensource@jensdiemer.de>
    :copyleft: 2018 by the django-for-runners team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from pathlib import Path

from django.test import TestCase
# https://github.com/jedie/django-tools
from django_tools.unittest_utils.assertments import assert_pformat_equal
from django_tools.unittest_utils.user import TestUserMixin

# https://github.com/jedie/django-for-runners
from for_runners.services.gpx_create import add_from_file, add_from_files, add_gpx


BASE_PATH = Path(__file__).parent


class GpxTests(TestUserMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.user = self._get_user(usertype="normal")

    def assert_garmin_connect_1_gpx(self, instance):
        print(instance)

        self.assertEqual(repr(instance), "<GpxModel: 2018-02-21 Moers>")

        self.assertEqual(instance.points_no, 3)
        self.assertEqual(round(instance.length, 3), 4.727)
        self.assertEqual(instance.duration_s, 2)
        self.assertEqual(round(instance.pace, 3), 7.052)
        self.assertEqual(instance.heart_rate_avg, 125)

        self.assertEqual(instance.get_short_slug(), "2018-02-21-moers")

    def test_add_gpx(self):
        filepath = Path(BASE_PATH, "fixture_files/garmin_connect_1.gpx")
        with filepath.open("r") as f:
            gpx_content = f.read()

        instance = add_gpx(gpx_content=gpx_content, user=self.user)
        self.assert_garmin_connect_1_gpx(instance)

    def test_add_from_file(self):
        instance = add_from_file(
            gpx_file_file_path=Path(BASE_PATH, "fixture_files/garmin_connect_1.gpx"), user=self.user
        )
        self.assert_garmin_connect_1_gpx(instance)

    def test_add_from_files(self):
        instances = [
            str(instance)
            for instance in add_from_files(
                gpx_files_file_path=Path(BASE_PATH, "fixture_files"),
                user=self.user,
                skip_errors=True,
            )
        ]
        assert_pformat_equal(
            instances, ["2018-02-21 Moers", "2011-01-13 Berlin Tiergarten"]
        )
