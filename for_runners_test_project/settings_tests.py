
"""
    Django settings used while pytest run
"""

from for_runners_test_project.settings import *


# https://bitbucket.org/kbr/autotask
#
# avoid:
#
# Error in atexit._run_exitfuncs:
# Traceback (most recent call last):
#   File ".../lib/python3.6/site-packages/autotask/apps.py", line 27, in __call__
#     self.delete_periodic_tasks()
#   File ".../lib/python3.6/site-packages/autotask/apps.py", line 37, in delete_periodic_tasks
#     if qs.count():
#   ...
# Failed: Database access not allowed, use the "django_db" mark, or the "db" or "transactional_db" fixtures to enable it.
AUTOTASK_IS_ACTIVE = False


# Skip download map via geotiler in for_runners.gpx_tools.gpxpy2map.generate_map
MAP_DOWNLOAD = False