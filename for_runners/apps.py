from pathlib import Path

import autocron
from django.apps import AppConfig as BaseAppConfig


class AppConfig(BaseAppConfig):
    name = 'for_runners'
    verbose_name = 'ForRunners'

    def ready(self):
        import for_runners.checks  # noqa

        # TODO: Remove after: https://github.com/kbr/autocron/issues/3
        Path('~/.autocron').expanduser().mkdir(parents=True, exist_ok=True)

        autocron.start('for_runner_autocron.sqlite')  # activate autocron with his SQLite database
