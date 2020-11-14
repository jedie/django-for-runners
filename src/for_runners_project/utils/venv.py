"""
    created 17.11.2018 by Jens Diemer <opensource@jensdiemer.de>
    :copyleft: 2018 by the django-for-runners team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import os
import sys
from pathlib import Path


class VirtualEnvPath:
    def __init__(self):
        # print("sys.executable:", sys.executable)
        # print("sys.prefix:", sys.prefix)
        # print("sys.real_prefix:", getattr(sys, "real_prefix", None))

        self.env_path = Path(sys.prefix)  # e.g.: /home/<username>/DjangoForRunnersEnv
        assert self.env_path.is_dir()

    def get_for_runners_exe(self):
        if sys.platform in ("win32", "cygwin"):
            for_runners_filename = "for_runners.exe"
        else:
            for_runners_filename = "for_runners"

        self.executable_path = Path(sys.executable)  # e.g.: /home/<username>/DjangoForRunnersEnv/bin/python3
        assert self.executable_path.is_file()

        # raise ValueError if self.env_path is not a subpath of self.executable_path
        self.executable_path.relative_to(self.env_path)

        for_runners_exe = Path(self.executable_path.parent, for_runners_filename)
        assert for_runners_exe.is_file(), "for_runner executeable not found here: '%s'" % for_runners_exe
        assert os.access(str(for_runners_exe), os.X_OK), "File not executeable: '%s'" % for_runners_exe

        return for_runners_exe


def get_venv_path():
    """
    :return: VirtualEnv root dir, e.g.: /home/<username>/DjangoForRunnersEnv
    """
    return VirtualEnvPath().env_path
