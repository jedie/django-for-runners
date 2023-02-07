import re
import shutil
import subprocess
from pathlib import Path

from bx_py_utils.auto_doc import assert_readme_block
from bx_py_utils.path import assert_is_file
from django.test import SimpleTestCase

import for_runners


def strip_ansi(output):
    return re.sub(r'\x1b\[\d+m', '', output)


class ReadmeTestCase(SimpleTestCase):
    def test_make_help(self):
        base_path = Path(for_runners.__file__).parent.parent
        assert_is_file(base_path / 'Makefile')
        readme_path = base_path / 'README.md'
        assert_is_file(readme_path)

        make_bin = shutil.which('make')
        output = subprocess.check_output(
            (make_bin, 'help'),
            stderr=subprocess.STDOUT,
            cwd=base_path,
            text=True,
        )
        output = strip_ansi(output)
        output = output.strip()
        output = '\n'.join(line for line in output.splitlines() if not line.startswith('make['))
        self.assertIn('List all commands', output)
        self.assertIn('fix-code-style', output)
        output = f'```\n{output}\n```'
        assert_readme_block(
            readme_path=readme_path,
            text_block=output,
            start_marker_line='[comment]: <> (✂✂✂ auto generated make help start ✂✂✂)',
            end_marker_line='[comment]: <> (✂✂✂ auto generated make help end ✂✂✂)',
        )
