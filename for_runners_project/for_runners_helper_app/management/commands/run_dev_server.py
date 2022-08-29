from django_tools.management.commands.run_testserver import Command as RunServerCommand

from for_runners.management.commands import fill_basedata
from for_runners.models import DistanceModel


class Command(RunServerCommand):
    help = "Run Django-ForRunners with django developer server"

    def post_setup(self, **options) -> None:
        self.stderr.write('_' * 79)
        self.stdout.write('Fill DistanceModel...')
        distance_model_count = DistanceModel.objects.all().count()
        if distance_model_count == 0:
            self.verbose_call(fill_basedata)
        else:
            self.stdout.write(f'Skip, DistanceModel contains {distance_model_count} entries, ok.')
