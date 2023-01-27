import sys

from django_rich.management import RichCommand
from manageprojects.utilities import code_style
from manageprojects.utilities.subprocess_utils import verbose_check_call

from manage_django_project.config import manage_config


class Command(RichCommand):
    help = 'Check/Fix project code style'

    def handle(self, *args, **options):
        verbose = options['verbosity'] > 1

        if verbose:
            self.console.print(f'\n[bold]{self.help}')

        manage_config.assert_initialized()

        color = not options['no_color']

        code_style._call_darker(package_root=manage_config.base_path, color=color, verbose=verbose)
        verbose_check_call(
            'flake8',
            *args,
            cwd=manage_config.base_path,
            exit_on_error=True,
        )
        print('Code style: OK')
        sys.exit(0)
