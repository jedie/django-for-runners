from pathlib import Path

from bx_py_utils.path import assert_is_file
from django_rich.management import RichCommand
from manageprojects.utilities.subprocess_utils import verbose_check_call


class Command(RichCommand):
    help = 'Run tests with coverage and report'

    def handle(self, *args, **options):
        self.console.print(f'\n[bold]{self.help}')

        cwd = Path.cwd()
        assert_is_file(cwd / 'pyproject.toml')

        verbose = options['verbosity'] > 0

        try:
            verbose_check_call('coverage', 'run', verbose=verbose, exit_on_error=True)
        except SystemExit as err:
            if err.code != 0:
                raise  # No report if tests fails

        verbose_check_call('coverage', 'combine', '--append', verbose=verbose, exit_on_error=True)
        verbose_check_call('coverage', 'report', verbose=verbose, exit_on_error=True)
        verbose_check_call('coverage', 'xml', verbose=verbose, exit_on_error=True)
        verbose_check_call('coverage', 'json', verbose=verbose, exit_on_error=True)
