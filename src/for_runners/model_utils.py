"""
    TODO: Move to django-tools
"""

from django.urls import reverse


class ModelAdminUrlMixin:
    def get_admin_change_url(self):
        return reverse(f"admin:{self._meta.app_label}_{self._meta.model_name}_change", args=(self.pk,))
