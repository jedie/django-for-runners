from django_rich.management import RichCommand
from rich.pretty import Pretty

from manage_django_project.config import manage_config


class Command(RichCommand):
    help = 'Just print information about the current Django project'

    def handle(self, *args, **options):
        self.console.print('\n[bold]Manage Django project information:')
        self.console.print('\nmanage_config = ', end='')
        self.console.print(Pretty(manage_config))
