from bx_django_utils.test_utils.html_assertion import HtmlAssertionMixin
from django.contrib.auth.models import User
from django.test import TestCase
from model_bakery import baker


class AdminEventParticipationTests(HtmlAssertionMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.superuser = baker.make(User, username='superuser', is_staff=True, is_active=True, is_superuser=True)

    def test_event_change_list(self):
        self.client.force_login(self.superuser)
        response = self.client.get("/en/admin/for_runners/eventmodel/", HTTP_ACCEPT_LANGUAGE="en")
        self.assertEqual(response.status_code, 200)
        self.assert_html_parts(
            response,
            parts=(
                "<strong>superuser</strong>",
                '<a href="/en/admin/for_runners/">ForRunners</a>',
                '<p class="paginator">0 Events</p>',
            ),
        )
        self.assertTemplateUsed(response, template_name="admin/for_runners/eventmodel/statistics.html")
        self.assertTemplateUsed(response, template_name="admin/for_runners/eventmodel/change_list.html")
