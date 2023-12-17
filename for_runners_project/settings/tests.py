# flake8: noqa: E405
"""
    Settings used to run tests
"""
import requests_mock

from for_runners_project.settings.prod import *  # noqa


# _____________________________________________________________________________
# Manage Django Project

INSTALLED_APPS.append('manage_django_project')

# _____________________________________________________________________________


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

SECRET_KEY = 'No individual secret for tests ;)'

DEBUG = True
PRINT_TRACEBACKS = True
RAISE_CAPTURE_EXCEPTIONS = True

# Speedup tests by change the Password hasher:
PASSWORD_HASHERS = ('django.contrib.auth.hashers.MD5PasswordHasher',)

# _____________________________________________________________________________
# Deny any real request in tests:


def _unmocked_requests_error_message(request, response):
    raise RuntimeError(f'Unmocked request to {request.url} in tests, wrap in  with requests_mock.mock() as m:')


fallback_mocker = requests_mock.Mocker()
fallback_mocker.get(requests_mock.ANY, content=_unmocked_requests_error_message)
fallback_mocker.__enter__()

# _____________________________________________________________________________

# Skip download map via geotiler in for_runners.gpx_tools.gpxpy2map.generate_map
MAP_DOWNLOAD = False


# All tests should use django-override-storage!
# Set root to not existing path, so that wrong tests will fail:
STATIC_ROOT = '/not/exists/static/'
MEDIA_ROOT = '/not/exists/media/'
