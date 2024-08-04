import io
import zipfile

import requests_mock
from bx_django_utils.test_utils.html_assertion import HtmlAssertionMixin
from django.contrib.auth.models import User
from django.test import TestCase
from model_bakery import baker
from override_storage import locmem_stats_override_storage

from for_runners import __version__
from for_runners.models import GpxModel
from for_runners.services.gpx_create import add_from_file
from for_runners.tests.fixture_files import get_fixture_path
from for_runners.tests.fixtures.openstreetmap import (
    OpenStreetMap5105254_244456Fixtures,
    OpenStreetMap5143785_661701Fixtures,
    OpenStreetMap5143789_661701Fixtures,
)
from for_runners.tests.mocks.weather_mock import WeatherMock


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

        gpx_file_path1 = get_fixture_path('garmin_connect_1.gpx')
        gpx_file_path2 = get_fixture_path('no_track_points.gpx')
        kml_file_path3 = get_fixture_path('PentaxK1.KML')

        with (
            gpx_file_path1.open("rb") as file1,
            gpx_file_path2.open("rb") as file2,
            kml_file_path3.open("rb") as file3,
            locmem_stats_override_storage() as storage_stats,
            requests_mock.mock() as m,
            WeatherMock() as weather_mock,
        ):
            m.get(**OpenStreetMap5143789_661701Fixtures().get_requests_mock_kwargs())

            # Start point lat=51.437889290973544 - lat=6.617012657225132:
            m.get(**OpenStreetMap5143785_661701Fixtures().get_requests_mock_kwargs())

            # End point lat=51.437847297638655 - lat=6.6170057002455:
            m.get(**OpenStreetMap5143789_661701Fixtures().get_requests_mock_kwargs())

            # lat=51.05254&lon=2.44456
            m.get(**OpenStreetMap5105254_244456Fixtures().get_requests_mock_kwargs())

            with self.assertLogs('for_runners'):
                response = self.client.post(
                    "/en/admin/for_runners/gpxmodel/upload/",
                    data={"files": [file1, file2, file3]},
                    HTTP_ACCEPT_LANGUAGE="en",
                )
            self.assertEqual(response.status_code, 302, response.content.decode())

            # debug_response(response)
            self.assertEqual(
                storage_stats.fields_saved,
                [
                    ('for_runners', 'gpxmodel', 'track_svg'),
                    ('for_runners', 'gpxmodel', 'gpx_file'),
                ],
            )
            assert storage_stats.fields_read == []

            existing_tracks = sorted(str(instance) for instance in GpxModel.objects.all())
            self.assertEqual(
                existing_tracks,
                [
                    '2018-02-21 Moers',
                    '2024-07-21 Leffrinckoucke, Nord',
                ],
            )

            track = GpxModel.objects.first()
            self.assertRedirects(
                response,
                expected_url=f"/en/admin/for_runners/gpxmodel/{track.pk:d}/change/",
                status_code=302,
                target_status_code=200,
                fetch_redirect_response=False,
            )

            self.assertEqual(
                weather_mock.call_data,
                [
                    {
                        'latitude': 51.437889290973544,
                        'longitude': 6.617012657225132,
                        'dt': '2018-02-21T14:30:50+00:00',
                    },
                    {
                        'latitude': 51.437847297638655,
                        'longitude': 6.6170057002455,
                        'dt': '2018-02-21T14:30:52+00:00',
                    },
                    {
                        'latitude': 51.05254,
                        'longitude': 2.444563,
                        'dt': '2024-07-21T14:30:24+01:00',
                    },
                    {
                        'latitude': 50.944859,
                        'longitude': 1.8479,
                        'dt': '2024-07-21T21:28:31+01:00',
                    },
                ],
            )

            response = self.client.get("/en/admin/for_runners/gpxmodel/", HTTP_ACCEPT_LANGUAGE="en")
        # print(repr(self.get_messages(response)))
        self.assert_html_parts(
            response,
            parts=(
                f"<title>Select GPX Track to change | Django-ForRunners v{__version__}</title>",
                '<li class="success">Created: 2018-02-21 Moers</li>',
                '<li class="success">Created: 2024-07-21 Leffrinckoucke, Nord</li>',
                '<td class="field-human_pace">7:03 min/km</td>',
                '<p class="paginator">2 GPX Tracks</p>',
            ),
        )
        self.assertTemplateUsed(response, template_name="admin/for_runners/gpxmodel/change_list.html")
        self.assert_messages(
            response,
            expected_messages=[
                'Process garmin_connect_1.gpx...',
                'Created: 2018-02-21 Moers',
                'Process no_track_points.gpx...',
                'Error process GPX data: No start time found!',
                'Process PentaxK1.KML...',
                'Created: 2024-07-21 Leffrinckoucke, Nord',
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

    def test_download_gpx_files(self):
        with locmem_stats_override_storage(), requests_mock.mock() as m, WeatherMock() as weather_mock:
            m.get(**OpenStreetMap5143785_661701Fixtures().get_requests_mock_kwargs())
            m.get(**OpenStreetMap5143789_661701Fixtures().get_requests_mock_kwargs())
            instance = add_from_file(track_path=get_fixture_path('garmin_connect_1.gpx'), user=self.superuser)

        self.assertEqual(instance.short_start_address, 'Moers')
        self.assertEqual(instance.get_short_slug(prefix_id=True), '20180221_1430_umd2rr-moers')

        self.client.force_login(self.superuser)
        response = self.client.post(
            path='/en/admin/for_runners/gpxmodel/',
            data={
                'action': 'download_gpx_files',
                'select_across': '0',
                'index': '0',
                '_selected_action': [instance.pk],
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/zip')

        zf = zipfile.ZipFile(io.BytesIO(response.content), 'r')
        self.assertEqual(
            zf.namelist(),
            ['20180221_1430_umd2rr-moers.gpx'],
        )
        self.assertEqual(
            weather_mock.call_data,
            [
                {
                    'latitude': 51.437889290973544,
                    'longitude': 6.617012657225132,
                    'dt': '2018-02-21T14:30:50+00:00',
                },
                {
                    'latitude': 51.437847297638655,
                    'longitude': 6.6170057002455,
                    'dt': '2018-02-21T14:30:52+00:00',
                },
            ],
        )
