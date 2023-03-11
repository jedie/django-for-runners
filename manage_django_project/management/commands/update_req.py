import sys
from pathlib import Path

from bx_py_utils.path import assert_is_file
from django_rich.management import RichCommand
from manageprojects.utilities.subprocess_utils import verbose_check_call


class Command(RichCommand):
    help = 'Update project requirements via pip-tools'

    def handle(self, *args, **options):
        self.console.print(f'\n[bold]{self.help}')

        cwd = Path.cwd()
        assert_is_file(cwd / 'pyproject.toml')
        assert_is_file(cwd / 'requirements.txt')
        assert_is_file(cwd / 'requirements.dev.txt')

        bin_path = Path(sys.executable).parent

        verbose_check_call(bin_path / 'pip', 'install', '-U', 'pip')
        verbose_check_call(bin_path / 'pip', 'install', '-U', 'pip-tools')

        extra_env = dict(
            CUSTOM_COMPILE_COMMAND='./manage.py update_req',
        )

        pip_compile_base = [
            bin_path / 'pip-compile',
            '--verbose',
            '--allow-unsafe',  # https://pip-tools.readthedocs.io/en/latest/#deprecations
            '--resolver=backtracking',  # https://pip-tools.readthedocs.io/en/latest/#deprecations
            '--upgrade',
            '--generate-hashes',
        ]

        # Only "prod" dependencies:
        verbose_check_call(
            *pip_compile_base,
            'pyproject.toml',
            '--output-file',
            'requirements.txt',
            extra_env=extra_env,
        )

        # dependencies + "dev"-optional-dependencies:
        verbose_check_call(
            *pip_compile_base,
            'pyproject.toml',
            '--extra=dev',
            '--output-file',
            'requirements.dev.txt',
            extra_env=extra_env,
        )

        verbose_check_call('safety', 'check', '-r', 'requirements.dev.txt')

        # Install new dependencies in current .venv:
        verbose_check_call('pip-sync', 'requirements.dev.txt')
