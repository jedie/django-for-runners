"""
    Base Django settings
"""

import logging
from pathlib import Path as __Path

from django.utils.translation import gettext_lazy as _

from for_runners.app_settings import *  # noqa


###############################################################################

# Build paths relative to the project root:
BASE_PATH = __Path(__file__).parent.parent.parent
print(f'BASE_PATH:{BASE_PATH}')
assert __Path(BASE_PATH, 'for_runners_project').is_dir()

###############################################################################


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False
PRINT_TRACEBACKS = False
RAISE_CAPTURE_EXCEPTIONS = False

# Serve static/media files by Django?
# In production the Webserver should serve this!
SERVE_FILES = False


# SECURITY WARNING: keep the secret key used in production secret!
__SECRET_FILE = __Path(BASE_PATH, 'secret.txt').resolve()
if not __SECRET_FILE.is_file():
    print(f'Generate {__SECRET_FILE}')
    from secrets import token_urlsafe as __token_urlsafe

    __SECRET_FILE.write_text(__token_urlsafe(128))

SECRET_KEY = __SECRET_FILE.read_text().strip()


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'bx_py_utils',  # https://github.com/boxine/bx_py_utils
    'import_export',  # https://github.com/django-import-export/django-import-export
    'dbbackup',  # https://github.com/django-dbbackup/django-dbbackup
    'adminsortable2',  # https://github.com/jrief/django-admin-sortable2
    'axes',  # https://github.com/jazzband/django-axes
    #
    # FIXME: https://github.com/jedie/django-processinfo/issues/19
    # 'django_processinfo',  # https://github.com/jedie/django-processinfo/
    #
    # https://github.com/jedie/django-tools/tree/master/django_tools/serve_media_app
    'django_tools.serve_media_app.apps.UserMediaFilesConfig',
    #
    # https://github.com/jedie/django-tools/tree/master/django_tools/model_version_protect
    # TODO: 'django_tools.model_version_protect.apps.ModelVersionProtectConfig',
    #
    # Django-ForRunners
    'for_runners_project.for_runners_helper_app',
    'for_runners.apps.AppConfig',
]

ROOT_URLCONF = 'for_runners_project.urls'
WSGI_APPLICATION = 'for_runners_project.wsgi.application'

AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesBackend',
    'django.contrib.auth.backends.ModelBackend',
]

MIDDLEWARE = [
    #
    # FIXME: https://github.com/jedie/django-processinfo/issues/19
    # 'django_processinfo.middlewares.ProcessInfoMiddleware',
    #
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'axes.middleware.AxesMiddleware',  # AxesMiddleware should be the last middleware
]

__TEMPLATE_DIR = __Path(BASE_PATH, 'for_runners_project', 'templates')
assert __TEMPLATE_DIR.is_dir(), f'Directory not exists: {__TEMPLATE_DIR}'
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        "DIRS": [str(__TEMPLATE_DIR)],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.media',
                'django.template.context_processors.csrf',
                'django.template.context_processors.tz',
                'django.template.context_processors.static',
                'for_runners.context_processors.for_runners_version_string',
            ],
        },
    },
]


DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

# _____________________________________________________________________________
# Internationalization

LANGUAGE_CODE = 'en'

LANGUAGES = [
    ('de', _('German')),
    ('en', _('English')),
]
USE_I18N = True
USE_L10N = True
TIME_ZONE = 'Europe/Paris'
USE_TZ = True

# _____________________________________________________________________________
# Static files (CSS, JavaScript, Images)

STATIC_URL = '/static/'
STATIC_ROOT = str(__Path(BASE_PATH, 'static'))

MEDIA_URL = '/media/'
MEDIA_ROOT = str(__Path(BASE_PATH, 'media'))

# _____________________________________________________________________________
# Cache Backend

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# _____________________________________________________________________________
# django-processinfo

from django_processinfo import app_settings as PROCESSINFO  # noqa


PROCESSINFO.ADD_INFO = False  # Don't add info in HTML page

# _____________________________________________________________________________
# Django-dbbackup

DBBACKUP_STORAGE = 'django.core.files.storage.FileSystemStorage'
DBBACKUP_STORAGE_OPTIONS = {'location': str(__Path(BASE_PATH, 'backups'))}


# _____________________________________________________________________________
# cut 'pathname' in log output

old_factory = logging.getLogRecordFactory()


def cut_path(pathname, max_length):
    if len(pathname) <= max_length:
        return pathname
    return f'...{pathname[-(max_length - 3):]}'


def record_factory(*args, **kwargs):
    record = old_factory(*args, **kwargs)
    record.cut_path = cut_path(record.pathname, 30)
    return record


logging.setLogRecordFactory(record_factory)

# -----------------------------------------------------------------------------

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'colored': {  # https://github.com/borntyping/python-colorlog
            '()': 'colorlog.ColoredFormatter',
            'format': '%(log_color)s%(asctime)s %(levelname)8s %(cut_path)s:%(lineno)-3s %(message)s',
        }
    },
    'handlers': {'console': {'class': 'colorlog.StreamHandler', 'formatter': 'colored'}},
    'loggers': {
        '': {'handlers': ['console'], 'level': 'DEBUG', 'propagate': False},
        'django': {'handlers': ['console'], 'level': 'INFO', 'propagate': False},
        'axes': {'handlers': ['console'], 'level': 'WARNING', 'propagate': False},
        'matplotlib': {'handlers': ['console'], 'level': 'INFO', 'propagate': False},
        'django_tools': {'handlers': ['console'], 'level': 'DEBUG', 'propagate': False},
        'for_runners': {'handlers': ['console'], 'level': 'DEBUG', 'propagate': False},
    },
}
