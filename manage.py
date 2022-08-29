#!/usr/bin/env python3
import os
import sys
from pathlib import Path


BASE_PATH = Path(__file__).parent


def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'for_runners_project.settings.local')

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            'Couldn\'t import Django. Are you sure it\'s installed and '
            'available on your PYTHONPATH environment variable? Did you '
            'forget to activate a virtual environment?'
        ) from exc
    try:
        execute_from_command_line(sys.argv)
    except Exception as err:
        from bx_py_utils.error_handling import print_exc_plus
        print_exc_plus(err)
        raise


if __name__ == '__main__':
    main()
