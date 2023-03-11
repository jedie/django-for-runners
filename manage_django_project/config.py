import dataclasses
from pathlib import Path
from types import ModuleType
from typing import Optional

from bx_py_utils.path import assert_is_file
from packaging.version import Version


try:
    import tomllib  # New in Python 3.11
except ImportError:
    import tomli as tomllib


@dataclasses.dataclass
class ManageConfig:
    initialized: bool = False

    module: Optional[ModuleType] = None
    module_version: Optional[Version] = None
    base_path: Optional[Path] = None
    pyproject_toml_path: Optional[Path] = None
    readme_path: Optional[Path] = None

    def initialize(self, mdp_module: ModuleType):
        self.module = mdp_module

        self.module_version = Version(mdp_module.__version__)

        self.base_path = Path(mdp_module.__file__).parent.parent

        self.pyproject_toml_path = Path(self.base_path, 'pyproject.toml')
        assert_is_file(self.pyproject_toml_path)

        self.readme_path = self.base_path / 'README.md'
        assert_is_file(self.readme_path)

        self.initialized = True

    def assert_initialized(self):
        assert self.initialized is True, f'Not initialized: {self}'

    def get_pyproject_toml(self) -> dict:
        self.assert_initialized()

        pyproject_toml = tomllib.loads(self.pyproject_toml_path.read_text(encoding='UTF-8'))
        return pyproject_toml


manage_config = ManageConfig()
