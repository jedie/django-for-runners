#!/usr/bin/env python3

import os
import sys

if sys.version_info < (3, 5):
    print("\nERROR: Python 3.5 or greater is required!\n")
    sys.exit(101)

if __name__ == "__main__":
    os.environ["DJANGO_SETTINGS_MODULE"] = "for_runners_test_project.settings"
    try:
        import django
    except ImportError as err:
        print("\nERROR:\n")
        import traceback
        traceback.print_exc()
        print("")
        print(" *** Couldn't import Django. ***")
        print(" *** Did you forget to activate a virtual environment? ***")
        print("")
        sys.exit(101)

    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
