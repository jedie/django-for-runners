import sys

from django_rich.management import RichCommand
from manageprojects.utilities.subprocess_utils import verbose_check_call


class Command(RichCommand):
    help = 'Run tests via tox'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.console.print(f'\n[bold]{self.help}')

        # Just pass everything to the origin tox CLI:

        verbose_check_call(sys.executable, '-m', 'tox', *sys.argv[2:])
        sys.exit(0)
