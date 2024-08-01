from bx_django_utils.test_utils.fixtures import fixtures_registry
from bx_py_utils.test_utils.datetime import parse_dt
from requests import PreparedRequest

from for_runners.tests.fixtures import BaseFixtures
from for_runners.weather import weather


def float_to_string(value):
    """
    >>> float_to_string(1.23)
    '123'
    """
    return str(value).replace('.', '')


class WeatherBaseFixtures(BaseFixtures):
    def __init__(self, *, latitude, longitude, dt):
        coordinates = f'{float_to_string(latitude)}_{float_to_string(longitude)}'
        self.file_name = f'weather_{coordinates}_{dt.date().isoformat()}.json'

        self.request_kwargs = weather._build_kwargs(latitude=latitude, longitude=longitude, dt=dt)
        url = self.request_kwargs['url']
        params = self.request_kwargs['params']  #

        # Build the same URL as the requests:
        prepared_request = PreparedRequest()
        prepared_request.prepare_url(url, params)
        self.url = prepared_request.url

        super().__init__()

    def renew(self):
        response = weather._make_request(**self.request_kwargs)
        data = response.json()
        self.store_fixture_data(data=data)


@fixtures_registry.register()
class Weather5141_678_20180621Fixtures(WeatherBaseFixtures):
    def __init__(self):
        super().__init__(
            latitude=51.4109,
            longitude=6.7828,
            dt=parse_dt('2018-06-21T14:30:24+01:00'),
        )


@fixtures_registry.register()
class WeatherWrongLatitudeFixtures(WeatherBaseFixtures):
    def __init__(self):
        super().__init__(
            latitude=91,  # Latitude must be in range of -90 to 90°
            longitude=0,
            dt=parse_dt('2024-07-01T18:10:02+01:00'),
        )
