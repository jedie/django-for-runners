"""
    Allow for_runners to be executable
    through `python -m for_runners`.
"""
from pathlib import Path

from manage_django_project.config import ManageConfig
from manage_django_project.manage import execute_django_from_command_line

import for_runners


def main():
    """
    entrypoint installed via pyproject.toml and [project.scripts] section.
    Must be set in ./manage.py and PROJECT_SHELL_SCRIPT
    """
    execute_django_from_command_line(
        config=ManageConfig(
            module=for_runners,
            project_root_path=Path(for_runners.__file__).parent.parent,
            prod_settings='for_runners_project.settings.prod',
            local_settings='for_runners_project.settings.local',
            test_settings='for_runners_project.settings.tests',
        )
    )


if __name__ == '__main__':
    main()
