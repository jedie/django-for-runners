# coding: utf-8



import pytest

# https://github.com/jedie/django-tools
from django_tools.unittest_utils.unittest_base import BaseTestCase
from django_tools.unittest_utils.user import TestUserMixin


@pytest.mark.django_db
class AdminAnonymousTests(BaseTestCase):
    """
    Anonymous will be redirected to the login page.
    """
    def test_login_en(self):
        response = self.client.get('/en/admin/', HTTP_ACCEPT_LANGUAGE='en')
        self.assertRedirects(response, expected_url='http://testserver/en/admin/login/?next=/en/admin/')

    def test_login_de(self):
        response = self.client.get('/de/admin/', HTTP_ACCEPT_LANGUAGE='de')
        self.assertRedirects(response, expected_url='http://testserver/de/admin/login/?next=/de/admin/')


@pytest.mark.django_db
class AdminLoggedinTests(TestUserMixin, AdminAnonymousTests):
    """
    Some basics test with the django admin
    """
    def test_staff_admin_index(self):
        self.login(usertype='staff')
        response = self.client.get('/en/admin/', HTTP_ACCEPT_LANGUAGE='en')
        self.assertResponse(response,
            must_contain=(
                'Django administration',
                'staff_test_user',
                'Site administration',
                'You don\'t have permission to edit anything.'
            ),
            must_not_contain=('error', 'traceback'),
            template_name='admin/index.html',
        )

    def test_superuser_admin_index(self):
        self.login(usertype='superuser')
        response = self.client.get('/en/admin/', HTTP_ACCEPT_LANGUAGE='en')
        self.assertResponse(response,
            must_contain=(
                'Django administration',
                'superuser',
                'Site administration',
                '/admin/auth/group/add/',
                '/admin/auth/user/add/',
            ),
            must_not_contain=('error', 'traceback'),
            template_name='admin/index.html',
        )
