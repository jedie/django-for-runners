from django.core.checks import Warning, register
from django.db import DatabaseError

from for_runners.models import DistanceModel


@register()
def distance_model_filled(app_configs, **kwargs):
    errors = []

    try:
        distance_model_count = DistanceModel.objects.all().count()
    except DatabaseError:
        # e.g.: migration not done, yet
        pass
    else:
        if distance_model_count == 0:
            errors.append(
                Warning(
                    'Distance model is empty!',
                    hint='Just call "./manage.py fill_basedata" manage command',
                    id='for_runners.W001',
                )
            )
    return errors
