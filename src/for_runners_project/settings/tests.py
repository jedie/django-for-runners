import tempfile as __tempfile
from for_runners_project.settings.base import *  # noqa


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

SECRET_KEY = 'No individual secret for tests ;)'

DEBUG = True

# _____________________________________________________________________________

# Skip download map via geotiler in for_runners.gpx_tools.gpxpy2map.generate_map
MAP_DOWNLOAD = False


# Store test files in temp directory
# TODO: All tests should mock this!
STATIC_ROOT = __tempfile.mkdtemp(prefix='for_runner_tests_')
MEDIA_ROOT = __tempfile.mkdtemp(prefix='for_runner_tests_')
# To find not mocked tests, use this:
# STATIC_ROOT = '/not/exists/static/'
# MEDIA_ROOT = '/not/exists/media/'
