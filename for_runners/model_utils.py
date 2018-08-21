"""
    TODO: Move to django-tools
"""

from django.urls import reverse


class ModelAdminUrlMixin:
    def get_admin_change_url(self):
        return reverse(
            'admin:{0}_{1}_change'.format(
                self._meta.app_label,
                self._meta.model_name,
            ),
            args=(self.pk,)
        )
