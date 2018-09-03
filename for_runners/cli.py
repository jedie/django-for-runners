#!/usr/bin/env python3

import os
import sys
import time

# https://github.com/jedie/django-for-runners
from for_runners.version import __version__

os.environ["DJANGO_SETTINGS_MODULE"] = "for_runners_test_project.settings"

# print("sys.real_prefix:", getattr(sys, "real_prefix", "-"))
# print("sys.prefix:", sys.prefix)

try:
    import django
    from django.core.management import call_command
except ImportError as err:
    print("\nERROR:\n")
    import traceback
    traceback.print_exc()
    print("")
    print(" *** Couldn't import Django. ***")
    print(" *** Did you forget to activate a virtual environment? ***")
    print("")
    sys.exit(101)

if sys.version_info < (3, 5):
    print("\nERROR: Python 3.5 or greater is required!\n")
    sys.exit(101)


def verbose_call(command):
    print("\n" * 3)
    print("_" * 79, file=sys.stderr, flush=True)
    print("Call %r\n" % command, flush=True)
    call_command(command)


def manage():
    """
    entry points used in setup.py for run django manage commands
    """
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)


def main():
    """
    entry points used in setup.py
    start the dev server
    """
    if "--version" in sys.argv:
        print(__version__)
        sys.exit(0)

    if len(sys.argv) > 1:
        print("Django-ForRunners v %s" % __version__)
        print("\nJust start this file without any arguments to run the dev. server ;)")
        print("Start with '--version' to see the Version number of the installed Django-ForRunners app\n")
        sys.exit(0)

    django.setup()
    try:
        while True:
            try:
                verbose_call("run_test_project_dev_server")
            except Exception as err:
                print("\nError: %s" % err)
            print("")
            print("\nRestart, Quit with CONTROL-C")
            for no in range(5, 1, -1):
                print("\tin %i sec..." % no)
                time.sleep(1)
    except KeyboardInterrupt:
        print("\nBye...")
        sys.exit(0)


if __name__ == "__main__":
    main()
