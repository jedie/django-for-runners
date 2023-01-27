import logging
from importlib import import_module

from django.conf import settings
from django.core.checks import Error, register

from manage_django_project.config import manage_config


log = logging.getLogger(__name__)


@register()
def init_manage_config(app_configs, **kwargs):
    errors = []

    try:
        mdp_module_name = settings.MANAGE_DJANGO_PROJECT_MODULE_NAME
    except AttributeError as err:
        msg = f'Can not get the module to be managed: {err}'
        log.exception(msg)
        errors.append(
            Error(
                msg=msg,
                hint='Add MANAGE_DJANGO_PROJECT_MODULE_NAME to your Django settings.',
                id='manage_django_project.E001',
            )
        )
    else:
        try:
            mdp_module = import_module(mdp_module_name)
        except ImportError as err:
            msg = f'Can not import settings.MANAGE_DJANGO_PROJECT_MODULE_NAME: {err}'
            log.exception(msg)
            errors.append(
                Error(
                    msg=msg,
                    hint='Update your Django settings.',
                    id='manage_django_project.E002',
                )
            )
        else:
            manage_config.initialize(mdp_module)

    return errors
