
"""
    ./manage.py load_dynamic_fixtures
"""
import logging

from django.conf import settings
from django.utils import translation

# https://github.com/Peter-Slump/django-dynamic-fixtures
from dynamic_fixtures.fixtures import BaseFixture
from for_runners.models import DisciplineModel

log = logging.getLogger(__name__)


class Fixture(BaseFixture):

    def load(self):
        print("_" * 79)
        print("Create DisciplineModel examples:")

        language_code = settings.LANGUAGE_CODE
        with translation.override(language_code):
            DisciplineModel.objects.get_or_create(name="Running")
