import os
import sys
from pathlib import Path

import click

# https://github.com/jedie/django-for-runners
import for_runners

SVG_LOGO = "static/Django-ForRunners.svg"  # .../for_runners/static/Django-ForRunners.svg

XDG_OPEN_FILENAME = "Django-ForRunners.desktop"
XDG_OPEN_TEMPLATE = """#!/usr/bin/env xdg-open

[Desktop Entry]
Version=1.0
Type=Application
Terminal=false
Icon={svg_logo_path}
Exec=x-terminal-emulator -e "{for_runners_exe} run_server && bash -i"
Name=Django-ForRunners
"""

# gnome-terminal -x bash -c '/usr/bin/cal && bash'


def get_env_path():
    """
    :return: VirtualEnv root dir, e.g.: /home/<username>/DjangoForRunnersEnv
    """
    # print("sys.executable:", sys.executable)
    # print("sys.prefix:", sys.prefix)
    # print("sys.real_prefix:", getattr(sys, "real_prefix", None))

    executable_path = Path(sys.executable)  # e.g.: /home/<username>/DjangoForRunnersEnv/bin/python3
    assert executable_path.is_file()
    env_path = Path(sys.prefix)  # e.g.: /home/<username>/DjangoForRunnersEnv
    assert env_path.is_dir()

    # raise ValueError if env_path is not a subpath of executable_path
    executable_path.relative_to(env_path)

    if sys.platform in ('win32', 'cygwin'):
        for_runners_filename = "for_runners.exe"
    else:
        for_runners_filename = "for_runners"

    for_runners_exe = Path(executable_path.parent, for_runners_filename)
    assert for_runners_exe.is_file(), "for_runner executeable not found here: '%s'" % for_runners_exe
    assert os.access(str(for_runners_exe), os.X_OK), "File not executeable: '%s'" % for_runners_exe

    return for_runners_exe, env_path


def get_for_runners_app_path():
    for_runners_app_path = Path(for_runners.__file__).parent
    return for_runners_app_path


def get_svg_logo_path():
    for_runners_app_path = get_for_runners_app_path()
    svg_logo_path = Path(for_runners_app_path, SVG_LOGO)
    assert svg_logo_path.is_file(), "Logo not found here: %s" % svg_logo_path
    return svg_logo_path


def create_linux_xdg_open_file(for_runners_exe, env_path):
    desktop_file_path = Path(env_path, XDG_OPEN_FILENAME)
    print("Create linux xdg-open starter here: %s" % desktop_file_path)

    svg_logo_path = get_svg_logo_path()
    content = XDG_OPEN_TEMPLATE.format(svg_logo_path=svg_logo_path, for_runners_exe=for_runners_exe)
    with desktop_file_path.open("w") as f:
        f.write(content)
    desktop_file_path.chmod(0o777)


def create_starter():
    click.echo("Create stater")
    for_runners_exe, env_path = get_env_path()
    print("Create starter in: %s" % env_path)

    if sys.platform in ('win32', 'cygwin'):
        raise NotImplementedError("TODO: Create starter under Windows!")
    else:
        create_linux_xdg_open_file(for_runners_exe, env_path)
