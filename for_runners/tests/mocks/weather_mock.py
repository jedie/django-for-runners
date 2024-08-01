from unittest.mock import patch

from for_runners.weather import weather


class WeatherMock:
    def __init__(self):
        self.call_data = []

    def __call__(self, **kwargs) -> tuple[float, str]:
        kwargs['dt'] = kwargs['dt'].isoformat()
        self.call_data.append(kwargs)
        number = len(self.call_data)

        temperature = 20 + number / 10
        weather_state = f'Partly cloudy (mocked {number})'

        return temperature, weather_state

    def __enter__(self):
        self.mock = patch.object(weather, 'coordinates2weather', self)
        self.mock.__enter__()
        return self

    def __exit__(self, *args):
        self.mock.__exit__(*args)
