"""
    created 21.06.2018 by Jens Diemer <opensource@jensdiemer.de>
    :copyleft: 2018 by the django-for-runners team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""
from for_runners.tests.base import BaseTestCase


class TestBase(BaseTestCase):

    def test_assert_equal_rounded(self):
        self.assert_equal_rounded(1.21, 1.22, decimal_places=1)
        self.assert_equal_rounded([1.57, 1.6], [1.6, 1.58], decimal_places=1)
        self.assert_equal_rounded((1.57, 1.6), (1.6, 1.58), decimal_places=1)
        with self.assertRaises(AssertionError):
            self.assert_equal_rounded(0.12345, 0.12346)
