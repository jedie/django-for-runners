from django_rich.management import RichCommand
from manageprojects.utilities.subprocess_utils import verbose_check_call


class Command(RichCommand):
    help = 'Run safety check against current requirements files'

    def handle(self, *args, **options):
        self.console.print(f'\n[bold]{self.help}')

        verbose_check_call('safety', 'check', '-r', 'requirements.dev.txt')
