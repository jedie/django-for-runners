#!/usr/bin/env python3

import os
import subprocess
import sys
import time

# https://github.com/jedie/django-for-runners
from for_runners.version import __version__

os.environ["DJANGO_SETTINGS_MODULE"] = "for_runners_project.settings"

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

    print(repr(print))
    print("_" * 79, file=sys.stderr, flush=True)
    print("call command %r\n" % command, flush=True)
    call_command(command)


def manage():
    """
    entry points used in setup.py for run django manage commands
    e.g.:
        ~$ ~/Django-ForRunners/bin/manage --version
    """
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)


def verbose_subprocess(command):
    """
    Call this script via subprocess, but with a "command" argument
    """
    print("\n" * 3)
    print("_" * 79, file=sys.stderr, flush=True)

    if sys.platform in ('win32', 'cygwin'):
        executable = "%s.exe" % sys.argv[0]
        args = [executable]
        # args == e.g.: ["C:\Program Files\Django-ForRunners\Scripts\for_runners.exe"]
    else:
        args = [sys.executable, sys.argv[0]]

    args.append(command)
    print("subprocess call %r\n" % args, flush=True)

    subprocess.check_call(args)


def run_dev_server():
    """
    run the django dev server in endless loop.

    entry points used in setup.py
    e.g.:
        ~$ ~/Django-ForRunners/bin/for_runners
    """
    if "--version" in sys.argv:
        print(__version__)
        sys.exit(0)

    if "--help" in sys.argv:
        print("Just start this file without any arguments to run the dev. server")
        sys.exit(0)

    if len(sys.argv) > 1:
        # call via verbose_subprocess():
        # run manage command:
        manage()
        sys.exit(0)

    while True:
        try:
            verbose_subprocess("makemigrations")  # helpfull for developing and add/change models ;)
            verbose_subprocess("migrate")
            verbose_subprocess("run_server")
        except Exception as err:
            print("\nError: %s" % err)
        except KeyboardInterrupt:
            pass

        print("")
        print("\nRestart, Quit with CONTROL-C")
        try:
            for no in range(5, 1, -1):
                print("\tin %i sec..." % no)
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\nExit by keyboard interrupt, ok.\n")
            sys.exit(0)

        # used in for_runners_project.for_runners_helper_app.management.commands.run_server.Command#run
        os.environ["DONT_OPEN_BROWSER"] = "yes"


if __name__ == "__main__":
    run_dev_server()
