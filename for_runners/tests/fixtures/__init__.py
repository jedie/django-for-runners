from pathlib import Path

from bx_django_utils.test_utils.fixtures import BaseFixtures as OriginBaseFixtures


FIXTURES_PATH = Path(__file__).parent


class BaseFixtures(OriginBaseFixtures):
    base_path = FIXTURES_PATH
    url = None

    def get_requests_mock_kwargs(self) -> dict:
        return {
            'url': self.url,
            'json': self.get_fixture_data(),
        }
