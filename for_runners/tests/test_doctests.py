from bx_py_utils.test_utils.unittest_utils import BaseDocTests

import for_runners


class DocTests(BaseDocTests):
    def test_doctests(self):
        self.run_doctests(
            modules=(for_runners,),
        )
