"""
    https://docs.djangoproject.com/en/2.0/ref/applications/#configuring-applications-ref

    created 04.07.2018 by Jens Diemer <opensource@jensdiemer.de>
    :copyleft: 2018 by the django-for-runners team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


from django.apps import AppConfig


class ForRunnersConfig(AppConfig):
    name = "for_runners"
    verbose_name = "ForRunners"
