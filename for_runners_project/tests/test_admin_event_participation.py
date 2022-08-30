import io

from bx_django_utils.test_utils.html_assertion import HtmlAssertionMixin
from django.contrib.auth.models import User
from django.test import TestCase
from django_tools.unittest_utils.mockup import ImageDummy
from model_bakery import baker
from override_storage import locmem_stats_override_storage

from for_runners.models import EventModel, ParticipationModel


class AdminEventParticipationTests(HtmlAssertionMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.superuser = baker.make(
            User, username='superuser', is_staff=True, is_active=True, is_superuser=True
        )

    def test_create_participation(self):
        self.client.force_login(self.superuser)

        event = baker.make(EventModel, name='Venloop')
        img = ImageDummy(width=1, height=1, format='png').in_memory_image_file(filename='test.png')
        upload = io.BytesIO(b'foobar')
        upload.name = 'certificate.pdf'

        with locmem_stats_override_storage() as storage_stats:
            response = self.client.post(
                path='/en/admin/for_runners/participationmodel/add/',
                HTTP_ACCEPT_LANGUAGE='en',
                data={
                    'event': f'{event.pk}',
                    'user': f'{self.superuser.pk}',
                    #
                    'distance_km': '21.0975',
                    'duration': '02:01:00',
                    'start_number': '1001',
                    'finisher_count': '10000',
                    #
                    'costs-TOTAL_FORMS': '2',
                    'costs-INITIAL_FORMS': '0',
                    'costs-MIN_NUM_FORMS': '0',
                    'costs-MAX_NUM_FORMS': '1000',
                    'costs-0-name': 'entry fee',
                    'costs-0-amount': '20',
                    #
                    'participationimagemodel_set-TOTAL_FORMS': '1',
                    'participationimagemodel_set-INITIAL_FORMS': '0',
                    'participationimagemodel_set-MIN_NUM_FORMS': '0',
                    'participationimagemodel_set-MAX_NUM_FORMS': '1000',
                    'participationimagemodel_set-0-position': '0',
                    'participationimagemodel_set-__prefix__-position': '0',
                    'participationimagemodel_set-0-image': img,
                    #
                    'participationfilemodel_set-TOTAL_FORMS': '1',
                    'participationfilemodel_set-INITIAL_FORMS': '0',
                    'participationfilemodel_set-MIN_NUM_FORMS': '0',
                    'participationfilemodel_set-MAX_NUM_FORMS': '1000',
                    'participationfilemodel_set-0-position': '0',
                    'participationfilemodel_set-0-file': upload,
                },
            )
        assert response.status_code == 302, response.content.decode('utf-8')  # Form error?
        self.assertRedirects(
            response,
            expected_url='/en/admin/for_runners/participationmodel/',
            fetch_redirect_response=False,
        )

        assert storage_stats.fields_saved == [
            ('for_runners', 'participationimagemodel', 'image'),
            ('for_runners', 'participationfilemodel', 'file'),
        ]
        assert storage_stats.fields_read == []

        assert ParticipationModel.objects.count() == 1
        instance = ParticipationModel.objects.first()
        assert (
            instance.verbose_name()
            == str(instance)
            == 'Venloop - superuser - 21.0975 km in 2:01:00'
        )
