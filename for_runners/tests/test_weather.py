"""
    Test API connection to metaweather.com via for_runners.weather

    https://www.metaweather.com/api/

    created 21.06.2018 by Jens Diemer <opensource@jensdiemer.de>
    :copyleft: 2018 by the django-for-runners team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import datetime

from for_runners.tests.base import BaseTestCase
from for_runners.weather import NoWeatherData, meta_weather_com


class WeatherTest(BaseTestCase):
    """
    TODO: Mock request!
    """

    def test(self):
        lat, lon = (51.4109, 6.7828)  # Duisburg -> WOEID: 648820 (Essen, city)
        date = datetime.datetime(year=2018, month=6, day=20, hour=20, minute=30)

        # Essen City on 21.06.2018
        # https://www.metaweather.com/de/648820/2018/6/20/
        temperature, weather_state = meta_weather_com.coordinates2weather(
            lat, lon, date=date, max_seconds=12 * 60 * 60
        )

        self.assert_equal_rounded(temperature, 25.41, decimal_places=2)
        self.assertEqual(weather_state, "Light Cloud/Showers")

    def test_small_max_seconds(self):
        lat, lon = (51.4109, 6.7828)  # Duisburg -> WOEID: 648820 (Essen, city)
        date = datetime.datetime(year=2018, month=6, day=20, hour=20, minute=30)

        # Essen City on 21.06.2018
        # https://www.metaweather.com/de/648820/2018/6/20/
        temperature, weather_state = meta_weather_com.coordinates2weather(lat, lon, date=date, max_seconds=0.1)

        self.assert_equal_rounded(temperature, 27.94, decimal_places=2)
        self.assertEqual(weather_state, "Light Cloud")

    def test_no_json_data(self):
        """
        Request weather for Essen City on 11.02.2017 will raise into 500 - Server error:
            https://www.metaweather.com/de/648820/2017/2/11/

        The API Request will return []:
            https://www.metaweather.com/api/location/648820/2017/2/11/

        MetaWeatherCom().location_day() will raise NoWeatherData
        """
        lat, lon = (51.4109, 6.7828)  # Duisburg -> WOEID: 648820 (Essen, city)
        date = datetime.datetime(year=2017, month=2, day=10, hour=12, minute=00)

        with self.assertRaises(NoWeatherData):
            temperature, weather_state = meta_weather_com.coordinates2weather(lat, lon, date=date)
