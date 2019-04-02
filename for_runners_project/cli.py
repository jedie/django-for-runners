#!/usr/bin/env python3

import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

import click

# https://github.com/jedie/django-for-runners
from for_runners.version import __version__
from for_runners_project.utils.gunicorn_server import get_gunicorn_application

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


def verbose_subprocess(*args, **kwargs):
    """
    Call this script via subprocess, but with a "command" argument
    """
    print("\n" * 3)
    print("_" * 79, file=sys.stderr, flush=True)
    click.echo("subprocess call '%s'\n" % click.style(" ".join(args), fg="green"))
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


@cli.command()
def run_server():
    """
    run the gunicorn server in endless loop.

    entry points used in setup.py
    e.g.:
        ~$ ~/Django-ForRunners/bin/for_runners run-server
    """
    subprocess_manage("makemigrations")  # helpfull for developing and add/change models ;)
    subprocess_manage("migrate")
    gunicorn_application = get_gunicorn_application()
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


@cli.command()
def update():
    """
    Update all packages in virtualenv.

    start with:
        $ for_runners update

    (Call this command only in a activated virtualenv.)
    """
    assert "VIRTUAL_ENV" in os.environ, "ERROR: Call me only in a activated virtualenv!"

    pip3_path = Path(sys.prefix, "bin", "pip3")
    if not pip3_path.is_file():
        print("ERROR: pip not found here: '%s'" % pip3_path)
        return

    print("pip found here: '%s'" % pip3_path)

    # Upgrade pip:
    verbose_subprocess(str(pip3_path), "install", "--upgrade", "pip")

    src_pkg_path = Path(__file__).parent.parent  # .../src/django-for-runners
    print(src_pkg_path)

    req_path = Path(src_pkg_path, "requirements.txt")
    if not req_path.is_file():
        print("ERROR: File not found: %s" % req_path)
        sys.exit(-1)

    # Update sources from git:
    if Path(src_pkg_path, ".git").is_dir():
        verbose_subprocess("git", "pull", "origin", "master", cwd=str(src_pkg_path))

    # upgrade requirements:
    verbose_subprocess(str(pip3_path), "install", "--upgrade", "-r", str(req_path))

    # install:
    verbose_subprocess(str(pip3_path), "install", "--upgrade", "-e", ".", cwd=str(src_pkg_path))

    print("\n\nYour virtual environment is updated!\n")


if __name__ == "__main__":
    cli()
