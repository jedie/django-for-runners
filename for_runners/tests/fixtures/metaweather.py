from bx_django_utils.test_utils.fixtures import fixtures_registry

from for_runners.tests.fixtures import BaseFixtures
from for_runners.weather import request_json


class MetaWeatherBaseFixtures(BaseFixtures):
    def renew(self):
        assert self.url
        if self.file_path.is_file():
            print(f'Skip {self.file_path}')
            return
        data = request_json(url=self.url)
        self.store_fixture_data(data=data)


@fixtures_registry.register()
class MetaWeather4695_744Fixtures(MetaWeatherBaseFixtures):
    file_name = 'metaweather_4695_744.json'
    url = 'https://www.metaweather.com/api/location/search/?lattlong=46.95,7.44'


@fixtures_registry.register()
class MetaWeather5144_662Fixtures(MetaWeatherBaseFixtures):
    file_name = 'metaweather_5144_662.json'
    url = 'https://www.metaweather.com/api/location/search/?lattlong=51.44,6.62'


@fixtures_registry.register()
class MetaWeather5141_678Fixtures(MetaWeatherBaseFixtures):
    file_name = 'metaweather_5141_678.json'
    url = 'https://www.metaweather.com/api/location/search/?lattlong=51.41,6.78'


@fixtures_registry.register()
class MetaWeather5252_1338Fixtures(MetaWeatherBaseFixtures):
    file_name = 'metaweather_5252_1338.json'
    url = 'https://www.metaweather.com/api/location/search/?lattlong=52.52,13.38'


@fixtures_registry.register()
class MetaWeather648820_2018_2_21Fixtures(MetaWeatherBaseFixtures):
    file_name = 'metaweather_location_648820_2018_2_21.json'
    url = 'https://www.metaweather.com/api/location/648820/2018/2/21/'


@fixtures_registry.register()
class MetaWeather648820_2018_6_20Fixtures(MetaWeatherBaseFixtures):
    file_name = 'metaweather_location_648820_2018_6_20.json'
    url = 'https://www.metaweather.com/api/location/648820/2018/6/20/'
