from pathlib import Path

import requests_mock
from bx_django_utils.test_utils.html_assertion import HtmlAssertionMixin
from django.contrib.auth.models import User
from django.test import TestCase
from model_bakery import baker
from override_storage import locmem_stats_override_storage

from for_runners import __version__
from for_runners.models import GpxModel
from for_runners.tests.fixture_files import FIXTURES_PATH
from for_runners.tests.fixtures.metaweather import (
    MetaWeather5144_662Fixtures,
    MetaWeather648820_2018_2_21Fixtures,
)
from for_runners.tests.fixtures.openstreetmap import (
    OpenStreetMap5143785_661701Fixtures,
    OpenStreetMap5143789_661701Fixtures,
)


class ForRunnerAdminTests(HtmlAssertionMixin, TestCase):
    """
    Special for runners admin tests
    """

    @classmethod
    def setUpTestData(cls):
        cls.superuser = baker.make(
            User, username='test-superuser', is_staff=True, is_active=True, is_superuser=True
        )

    def test_staff_upload(self):
        self.client.force_login(self.superuser)

        gpx_file_path1 = Path(FIXTURES_PATH, "garmin_connect_1.gpx")
        gpx_file_path2 = Path(FIXTURES_PATH, "no_track_points.gpx")

        with gpx_file_path1.open("rb") as file1, gpx_file_path2.open(
            "rb"
        ) as file2, locmem_stats_override_storage() as storage_stats, requests_mock.mock() as m:
            m.get(**MetaWeather5144_662Fixtures().get_requests_mock_kwargs())
            m.get(**MetaWeather648820_2018_2_21Fixtures().get_requests_mock_kwargs())

            m.get(**OpenStreetMap5143789_661701Fixtures().get_requests_mock_kwargs())

            # Start point lat=51.437889290973544 - lat=6.617012657225132:
            m.get(**OpenStreetMap5143785_661701Fixtures().get_requests_mock_kwargs())

            # End point lat=51.437847297638655 - lat=6.6170057002455:
            m.get(**OpenStreetMap5143789_661701Fixtures().get_requests_mock_kwargs())

            response = self.client.post(
                "/en/admin/for_runners/gpxmodel/upload/",
                data={"gpx_files": [file1, file2]},
                HTTP_ACCEPT_LANGUAGE="en",
            )
            # debug_response(response)
            assert storage_stats.fields_saved == [
                ('for_runners', 'gpxmodel', 'track_svg'),
                ('for_runners', 'gpxmodel', 'gpx_file'),
            ]
            assert storage_stats.fields_read == []

            tracks = GpxModel.objects.all()
            self.assertEqual(tracks.count(), 1)
            new_track = tracks[0]

            self.assertRedirects(
                response,
                expected_url=f"/en/admin/for_runners/gpxmodel/{new_track.pk:d}/change/",
                status_code=302,
                target_status_code=200,
                fetch_redirect_response=False,
            )

            response = self.client.get("/en/admin/for_runners/gpxmodel/", HTTP_ACCEPT_LANGUAGE="en")
            # print(repr(self.get_messages(response)))
            self.assert_html_parts(
                response,
                parts=(
                    f"<title>Select GPX Track to change | Django-ForRunners v{__version__}</title>",
                    # "Process garmin_connect_1.gpx...",
                    # "Created: 2018-02-21 14:30:50 Moers",
                    #
                    # "Process no_track_points.gpx...",
                    # "Error process GPX data: Can't get first track",
                    '<td class="field-human_pace">7:03 min/km</td>',
                    '<p class="paginator">1 GPX Track</p>',
                ),
            )
            self.assertTemplateUsed(
                response, template_name="admin/for_runners/gpxmodel/change_list.html"
            )
            self.assert_messages(
                response,
                expected_messages=[
                    "Process garmin_connect_1.gpx...",
                    "Created: 2018-02-21 Moers",
                    "Process no_track_points.gpx...",
                    "Error process GPX data: Can't get first track",
                ],
            )

            assert storage_stats.fields_read == []

    def test_add_view_redirect_to_upload(self):
        self.client.force_login(self.superuser)
        response = self.client.get("/en/admin/for_runners/gpxmodel/add/", HTTP_ACCEPT_LANGUAGE="en")
        self.assertRedirects(
            response,
            expected_url="/en/admin/for_runners/gpxmodel/upload/",
            status_code=302,
            target_status_code=200,
            fetch_redirect_response=True,
        )
