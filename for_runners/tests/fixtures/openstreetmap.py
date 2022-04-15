from bx_django_utils.test_utils.fixtures import fixtures_registry

from for_runners.tests.fixtures import BaseFixtures
from for_runners.weather import request_json


class OpenStreetMapBaseFixtures(BaseFixtures):
    def renew(self):
        assert self.url
        if self.file_path.is_file():
            print(f'Skip {self.file_path}')
            return
        data = request_json(url=self.url)
        self.store_fixture_data(data=data)


@fixtures_registry.register()
class OpenStreetMap0_0Fixtures(OpenStreetMapBaseFixtures):
    file_name = 'osm_0_0.json'
    url = (
        'https://nominatim.openstreetmap.org/reverse'
        '?lat=0.0&lon=0.0&format=json&addressdetails=1&zoom=17'
    )


@fixtures_registry.register()
class OpenStreetMap5143789_661701Fixtures(OpenStreetMapBaseFixtures):
    file_name = 'osm_5143789_661701.json'
    url = (
        'https://nominatim.openstreetmap.org/reverse'
        '?lat=51.43789&lon=6.61701&format=json&addressdetails=1&zoom=17'
    )


@fixtures_registry.register()
class OpenStreetMap5143785_661701Fixtures(OpenStreetMapBaseFixtures):
    file_name = 'osm_5143785_661701.json'
    url = (
        'https://nominatim.openstreetmap.org/reverse'
        '?lat=51.43785&lon=6.61701&format=json&addressdetails=1&zoom=17'
    )


@fixtures_registry.register()
class OpenStreetMap51437889_66617012Fixtures(OpenStreetMapBaseFixtures):
    file_name = 'osm_51437889_66617012.json'
    url = (
        'https://nominatim.openstreetmap.org/reverse'
        '?lat=51.437889290973544&lon=6.617012657225132'
        '&format=json&addressdetails=1&zoom=17'
    )
