"""
    API connection to open-meteo.com

    https://open-meteo.com/en/docs/historical-weather-api

    created 21.06.2018 by Jens Diemer <opensource@jensdiemer.de>
    :copyleft: 2018-2024 by the django-for-runners team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""
import datetime
import logging
import time
from pprint import pprint

from bx_py_utils.test_utils.datetime import parse_dt
from requests import HTTPError, RequestException

from for_runners.request_session import request_get


log = logging.getLogger(__name__)


WMO_CODE_DESCRIPTIONS = {  # World Meteorological Organization code descriptions
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Drizzle: Light",
    53: "Drizzle: Moderate",
    55: "Drizzle: Dense intensity",
    56: "Freezing Drizzle: Light",
    57: "Freezing Drizzle: Dense intensity",
    61: "Rain: Slight",
    63: "Rain: Moderate",
    65: "Rain: Heavy intensity",
    66: "Freezing Rain: Light",
    67: "Freezing Rain: Heavy intensity",
    71: "Snow fall: Slight",
    73: "Snow fall: Moderate",
    75: "Snow fall: Heavy intensity",
    77: "Snow grains",
    80: "Rain showers: Slight",
    81: "Rain showers: Moderate",
    82: "Rain showers: Violent",
    85: "Snow showers: Slight",
    86: "Snow showers: Heavy",
    95: "Thunderstorm: Slight or moderate",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}


def tzinfo_to_gmt_string(tzinfo):
    """
    >>> tzinfo_to_gmt_string(datetime.timezone(datetime.timedelta(hours=-14)))
    'Etc/GMT-14'

    >>> from zoneinfo import ZoneInfo
    >>> tzinfo_to_gmt_string(ZoneInfo('Europe/Berlin'))
    'Etc/GMT+2'
    """
    offset = tzinfo.utcoffset(datetime.datetime.now())
    hours = int(offset.total_seconds() // 3600)
    sign = '+' if hours >= 0 else '-'
    return f'Etc/GMT{sign}{abs(hours)}'


class NoWeatherData(ValueError):
    pass


class Weather:

    def _request(self, url, *, params) -> dict | None:
        log.info(f'Request {url=} {params=})')
        start_time = time.time()
        try:
            response = request_get(url, params=params)
            data = response.json()
            if data.get('error'):
                raise NoWeatherData(f'{data["reason"]} ({url=} {params=})')
            response.raise_for_status()
        except NoWeatherData:
            raise
        except (HTTPError, RequestException, ValueError) as err:
            log.exception(f'ERROR: {err} ({url=} {params=})')
            raise NoWeatherData(err)
        else:
            response_time_ms = round((time.time() - start_time) * 1000, 1)
            log.info(f"Response in: {response_time_ms:.1f}ms ({url=} {params=})")
            return data

    def _build_kwargs(self, *, latitude: float, longitude: float, dt: datetime.datetime) -> dict:
        url = 'https://archive-api.open-meteo.com/v1/archive'
        date = dt.date().isoformat()
        params = {
            'latitude': latitude,
            'longitude': longitude,
            'start_date': date,
            'end_date': date,
            'hourly': [
                'temperature_2m',
                'weather_code',
                # TODO: Add 'wind_gusts_10m' ???
            ],
        }
        if tzinfo := dt.tzinfo:
            timezone_name = tzinfo_to_gmt_string(tzinfo)
            params['timezone'] = timezone_name

        return dict(url=url, params=params)

    def _raw_data(self, *, latitude: float, longitude: float, dt: datetime.datetime) -> dict:
        request_kwargs = self._build_kwargs(latitude=latitude, longitude=longitude, dt=dt)
        data = self._request(**request_kwargs)
        return data

    def coordinates2weather(self, *, latitude: float, longitude: float, dt: datetime.datetime) -> tuple[float, str]:
        data = self._raw_data(latitude=latitude, longitude=longitude, dt=dt)
        # data = {
        #     'elevation': 45.0,
        #     'generationtime_ms': 0.06699562072753906,
        #     'hourly': {
        #         'temperature_2m': [
        #             17.3,
        #             16.7,
        #             #...
        #             11.2,
        #             10.6,
        #         ],
        #         'time': [
        #             '2018-06-21T00:00',
        #             '2018-06-21T01:00',
        #             #...
        #             '2018-06-21T22:00',
        #             '2018-06-21T23:00',
        #         ],
        #         'weather_code': [0, 0, 0, 0, 3, 51, 53, 51, 51, 2, 1, 1, 1, 1, 3, 3, 3, 1, 1, 1, 1, 1, 1, 1],
        #     },
        #     'hourly_units': {
        #         'temperature_2m': '°C',
        #         'time': 'iso8601',
        #         'weather_code': 'wmo code',
        #     },
        #     'latitude': 51.42355,
        #     'longitude': 6.8354435,
        #     'timezone': 'Etc/GMT+1',
        #     'timezone_abbreviation': '-01',
        #     'utc_offset_seconds': -3600,
        # }

        # Check some data:
        times = data['hourly']['time']
        try:
            assert len(times) == 24
            assert data['hourly_units']['temperature_2m'] == '°C'
            assert data['hourly_units']['weather_code'] == 'wmo code'
            assert data['hourly_units']['time'] == 'iso8601'

            hour = dt.hour
            assert isinstance(hour, int)

            # Just check if the index is correct:
            time_str = times[hour]
            assert time_str.endswith(f'{hour:02d}:00'), f'{time_str=} {hour=} {times=}'
        except AssertionError:
            pprint(data)
            raise

        temperature = data['hourly']['temperature_2m'][hour]
        wmo_code = data['hourly']['weather_code'][hour]
        try:
            weather_state = WMO_CODE_DESCRIPTIONS[wmo_code]
        except KeyError:
            raise KeyError(f'Unknown: {wmo_code=}')

        return temperature, weather_state


weather = Weather()

if __name__ == "__main__":
    # Duisburg on 21.06.2018
    # https://www.google.de/maps/@51.4109,6.7828,12z
    # https://open-meteo.com/en/docs/historical-weather-api#latitude=51.4109&longitude=6.7828&start_date=2018-06-21&end_date=2018-06-21&hourly=temperature_2m,weather_code,wind_gusts_10m&daily=&timezone=Europe%2FBerlin
    temperature, weather_state = weather.coordinates2weather(
        latitude=51.4109, longitude=6.7828, dt=parse_dt('2018-06-21T14:30:24+01:00')
    )
    print(temperature, weather_state)
    assert temperature == 16.4, f'{temperature=}'
    assert weather_state == 'Overcast', f'{weather_state=}'
