import shutil
from pathlib import Path
from unittest import TestCase

# https://github.com/jedie/django-tools
from django_tools.unittest_utils.django_command import DjangoCommandMixin


class ForRunnersCommandTestCase(DjangoCommandMixin, TestCase):
    @classmethod
    def setUpClass(cls):
        # installed via setup.py entry points !
        cls.for_runners_bin = shutil.which("for_runners")
        cls.manage_bin = shutil.which("manage")

    def _call_for_runners(self, cmd, **kwargs):
        for_runners_path = Path(self.for_runners_bin)
        return self.call_manage_py(
            cmd=cmd,
            manage_dir=str(for_runners_path.parent),
            manage_py=for_runners_path.name,  # Python 3.5 needs str()
            **kwargs
        )

    def _call_manage(self, cmd, **kwargs):
        manage_path = Path(self.manage_bin)
        return self.call_manage_py(
            cmd=cmd,
            manage_dir=str(manage_path.parent),
            manage_py=manage_path.name,  # Python 3.5 needs str()
            **kwargs
        )
