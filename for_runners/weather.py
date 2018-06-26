"""
    API connection to metaweather.com

    https://www.metaweather.com/api/#locationday
    https://www.metaweather.com/api/location/search/?lattlong=36.96,-122.02
    https://www.metaweather.com/api/location/2487956/2013/4/30/

    created 21.06.2018 by Jens Diemer <opensource@jensdiemer.de>
    :copyleft: 2018 by the django-for-runners team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""
import collections
import datetime
import json
import logging
import socket
import statistics
import time
import urllib
import urllib.request
from pprint import pprint
from urllib.error import URLError

log = logging.getLogger(__name__)

class NoWeatherData(ValueError):
    pass


def request_json(url, timeout=3, user_agent="python"):
    request = urllib.request.Request(url)
    request.add_header('User-Agent', user_agent)

    start_time = time.time()
    try:
        with urllib.request.urlopen(request, timeout=timeout) as f:
            json_data = f.read()
    except (URLError, socket.timeout) as err:
        print("ERROR: %s (url: %r)" % (err, url))
        raise NoWeatherData
    else:
        response_time_ms = round((time.time() - start_time) * 1000, 1)
        print("Response in: %.1fms (url: %r)" % (response_time_ms, url))
        data = json.loads(json_data)
        return data



class MetaWeatherCom:

    API_URL = "https://www.metaweather.com/api"

    def _request(self, url):
        url = self.API_URL + url
        data = request_json(url)
        return data

    _lat_lon2woeid_cache = {}
    def lat_lon2woeid(self, lat, lon, decimal_places=2):
        """
        lat/lon coordinates to WOEID (Where On Earth ID)

        :return: nearest woeid, json_data
        """
        lat = round(lat, decimal_places)
        lon = round(lon, decimal_places)

        try:
            result = self._lat_lon2woeid_cache[(lat, lon)]
            log.info("Fetch WOEID from cache!")
            return result
        except KeyError:
            log.info("Request WOEID")

        json_data = self._request(url="/location/search/?lattlong=%s,%s" % (lat, lon))
        # pprint(json_data)
        # [{'distance': 1836,
        #   'latt_long': '36.974018,-122.030952',
        #   'location_type': 'City',
        #   'title': 'Santa Cruz',
        #   'woeid': 2488853},
        #  {'distance': 43722,
        #   'latt_long': '37.338581,-121.885567',
        #   'location_type': 'City',
        #   'title': 'San Jose',
        #   'woeid': 2488042},
        #  {'distance': 49177,
        #   'latt_long': '37.39999,-122.079552',
        #   'location_type': 'City',
        #   'title': 'Mountain View',
        #   'woeid': 2455920},
        #  ...]
        last_distance = None
        nearest_woeid = None
        woe_data = None
        for result in json_data:
            distance = int(result["distance"])
            if last_distance is None or distance < last_distance:
                last_distance = distance
                woe_data = result
                nearest_woeid = int(woe_data["woeid"])

        result = (nearest_woeid, woe_data, json_data)
        self._lat_lon2woeid_cache[(lat, lon)] = result
        return result

    _location_day_cache = {}
    def location_day(self, woeid, date, max_seconds=60):

        url = "/location/{woeid}/{year}/{month}/{day}/".format(
            woeid=woeid, year=date.year, month=date.month, day=date.day
        )
        try:
            json_data = self._location_day_cache[url]
        except KeyError:
            log.debug("Request %s...", url)
            json_data = self._request(url)
            self._location_day_cache[url] = json_data
        else:
            log.debug("Fetch %s from cache!", url)

        if not json_data:
            log.error("json response is empty")
            raise NoWeatherData("json response is empty")

        # pprint(json_data)
        # [{'air_pressure': 1005.36,
        # 'applicable_date': '2017-04-30',
        # 'created': '2017-05-01T07:19:02.690650Z',
        # 'humidity': 55,
        # 'id': 6301075443286016,
        # 'max_temp': 23.453333333333333,
        # 'min_temp': 10.014999999999999,
        # 'predictability': 70,
        # 'the_temp': 23.97666666666667,
        # 'visibility': 12.81857701026008,
        # 'weather_state_abbr': 'lc',
        # 'weather_state_name': 'Light Cloud',
        # 'wind_direction': 305.4904669344955,
        # 'wind_direction_compass': 'NW',
        # 'wind_speed': 5.540785988894192},
        # ...]
        data = collections.defaultdict(list)
        for result in json_data:
            created_string = result["created"]  # e.g.: 2018-06-20T22:30:29.227960Z
            created_datetime = datetime.datetime.strptime(created_string, "%Y-%m-%dT%H:%M:%S.%fZ")

            delta = abs(date - created_datetime)
            data[delta.total_seconds()] = result

        temperatures = []
        weather_state_counter = collections.Counter()
        for delta_seconds, result in sorted(data.items()):
            if len(temperatures)>0 and delta_seconds > max_seconds:
                # Skip if "created" date time is more than max_seconds, but collect at least one result
                continue

            temperature = statistics.median([result["min_temp"], result["the_temp"], result["max_temp"]])
            log.debug("Collect %.1f°C from %s (delta: %isec)", temperature, result["created"], delta_seconds)
            temperatures.append(temperature)

            weather_state_counter[result["weather_state_name"]] += 1

            # print("%s°C" % round(temperature), created_datetime, delta, delta_hours)

        temperature = statistics.median(temperatures)

        # print(weather_state_counter) # e.g.: Counter({'Light Cloud': 5, 'Showers': 2, 'Heavy Cloud': 1})
        weather_states = [item[0] for item in weather_state_counter.most_common()] # e.g.: ['Light Cloud', 'Showers', 'Heavy Cloud']
        # print(weather_states)
        weather_state = "/".join(weather_states[:2]) # e.g.: Light Cloud/Showers

        log.info("Result: %.1f°C %r", temperature, weather_state)

        return temperature, weather_state

        #
        # print(
        #     created_datetime,
        #     "%s°C" % round(result["min_temp"]),
        #     "%s°C" % round(result["the_temp"]),
        #     "%s°C" % round(result["max_temp"]),
        #     "-> %s°C" % round(temp),
        #     result["predictability"],
        #     result["weather_state_name"],
        # )

    def coordinates2weather(self, lat, lon, date, max_seconds=12):
        if date is None:
            raise NoWeatherData("Can't get weather if date is None!")

        nearest_woeid, woe_data, json_data = self.lat_lon2woeid(lat, lon)
        log.info("Use nearest WOEID: %i (%r)", nearest_woeid, woe_data)
        temperature, weather_state = self.location_day(woeid=nearest_woeid, date=date, max_seconds=max_seconds)
        return temperature, weather_state


meta_weather_com = MetaWeatherCom()


if __name__ == "__main__":
    # Duisburg:
    # https://www.metaweather.com/api/location/search/?lattlong=51.4109,6.7828
    # woeid=648820 # Essen, city

    # nearest_woeid, woe_data, json_data = MetaWeatherCom().lat_lon2woeid(36.96, -122.02)
    # print("woeid:", nearest_woeid, woe_data) # woeid: 2488853 {'distance': 1836, 'title': 'Santa Cruz', 'location_type': 'City', 'woeid': 2488853, 'latt_long': '36.974018,-122.030952'}

    # /api/location/2487956/2013/4/30/ - San Francisco on 30th April 2013
    # MetaWeatherCom().location_day(woeid=2488853, date=datetime.date(year=2017, month=4, day=30))

    # Essen City on 21.06.2018
    # https://www.metaweather.com/de/648820/2018/6/20/
    temperature, weather_state = meta_weather_com.coordinates2weather(51.4109,6.7828, date=datetime.datetime(year=2018, month=6, day=20, hour=20, minute=30))
    temperature, weather_state = meta_weather_com.coordinates2weather(51.4109,6.7828, date=datetime.datetime(year=2018, month=6, day=20, hour=13, minute=30))
    temperature, weather_state = meta_weather_com.coordinates2weather(51.4109,6.7828, date=datetime.datetime(year=2018, month=6, day=20, hour=4, minute=30))
    temperature, weather_state = meta_weather_com.coordinates2weather(51.4109,6.7828, date=datetime.datetime(year=2018, month=6, day=20, hour=20, minute=30))