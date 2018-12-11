"""
    https://django-import-export.readthedocs.io/en/latest/getting_started.html
"""

from import_export import resources

# https://github.com/jedie/django-for-runners
from for_runners.models import GpxModel


class GpxModelResource(resources.ModelResource):

    class Meta:
        model = GpxModel
        exclude = ("gpx",)
