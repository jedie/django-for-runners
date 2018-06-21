"""
    created 21.06.2018 by Jens Diemer <opensource@jensdiemer.de>
    :copyleft: 2018 by the django-for-runners team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import unittest


class BaseTestCase(unittest.TestCase):

    def assert_equal_rounded(self, value1, value2, decimal_places=5, msg=None):

        if isinstance(value1, (tuple, list)):
            value1 = [round(v, decimal_places) for v in value1]
            value2 = [round(v, decimal_places) for v in value2]
        else:
            value1 = round(value1, decimal_places)
            value2 = round(value2, decimal_places)
        self.assertEqual(value1, value2, msg=msg)
