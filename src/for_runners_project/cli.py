#!/usr/bin/env python3

import os

import subprocess
import sys
import time


import click

# https://github.com/jedie/django-for-runners
from for_runners import __version__
from for_runners_project.utils.gunicorn_server import get_gunicorn_application


os.environ["DJANGO_SETTINGS_MODULE"] = "for_runners_project.settings"

# print("sys.real_prefix:", getattr(sys, "real_prefix", "-"))
# print("sys.prefix:", sys.prefix)

try:
    import django
    from django.core.management import call_command
except ImportError as err:
    print(f"\nERROR: {err}\n")
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


def verbose_subprocess(*args, **kwargs):
    """
    Call this script via subprocess, but with a "command" argument
    """
    print("\n" * 3)
    print("_" * 79, file=sys.stderr, flush=True)
    click.echo(f"subprocess call '{click.style(' '.join(args), fg='green')}'\n")
    subprocess.check_call(args, **kwargs)


def subprocess_manage(*args):
    """
    Call django manage command via:
        for_runners_project/__main__.py
    """
    args = [sys.executable, "-m", "for_runners_project"] + list(args)
    verbose_subprocess(*args)


def call_manage_command(*, cmd_class):
    cmd = cmd_class.Command()
    call_command(cmd)


@click.group()
@click.version_option(__version__, prog_name="Django-ForRunners")
def cli():
    print("Start up...")


@cli.command()
def run_dev_server():
    """
    run the django dev server in endless loop.

    entry points used in setup.py
    e.g.:
        ~$ ~/Django-ForRunners/bin/for_runners run-server
    """
    while True:
        try:
            subprocess_manage("makemigrations")  # helpfull for developing and add/change models ;)
            subprocess_manage("migrate")
            subprocess_manage("run_server")
        except Exception as err:
            print(f"\nError: {err}")
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


@cli.command()
@click.argument("address", nargs=1, default="127.0.0.1:8000")
def run_server(address):
    """
    Run the gunicorn server in endless loop.
    e.g.:

    ~$ for_runners run-server

    ~$ for_runners run-server 127.0.0.1:8080
    """
    subprocess_manage("makemigrations")  # helpfull for developing and add/change models ;)
    subprocess_manage("migrate")
    gunicorn_application = get_gunicorn_application(address)
    gunicorn_application.run()


@cli.command()
def create_starter():
    """
    Create starter file.
    """
    django.setup()
    from for_runners_project.starter import create_starter

    create_starter()


@cli.command()
def recreate_files():
    """
    Recreate all SVG and GPX files for all Tracks.
    """
    django.setup()
    from for_runners.management.commands import recreate_files

    call_manage_command(cmd_class=recreate_files)


@cli.command()
def backup():
    """
    Backup everything
    """
    django.setup()
    from for_runners.management.commands import backup

    call_manage_command(cmd_class=backup)


if __name__ == "__main__":
    cli()
