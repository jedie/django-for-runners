#!/usr/bin/env python3

import os
import sys


def main():
    assert 'DJANGO_SETTINGS_MODULE' in os.environ, 'No "DJANGO_SETTINGS_MODULE" in environment!'
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
