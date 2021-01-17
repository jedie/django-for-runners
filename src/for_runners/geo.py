"""
    created 31.05.2018 by Jens Diemer <opensource@jensdiemer.de>
    :copyleft: 2018-2020 by the django-for-runners team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""
import collections
import logging

from django.core.cache import cache
from geopy.geocoders import Nominatim


log = logging.getLogger(__name__)

WGS84_NDIGITS = 5

Address = collections.namedtuple("Address", ("short, full"))


def construct_short_address(address):
    log.debug(f'address={address}')
    parts = []

    if "village" in address and "county" in address:
        parts.append(f"{address['village']},")
        parts.append(address["county"])
    else:
        parts.append(
            address.get("city") or address.get("town")
            or address.get("county") or address.get("state")
        )
        parts.append(address.get("suburb"))

    results = []
    for part in parts:
        if part and part not in results:
            results.append(part)

    short_address = " ".join(results)
    return short_address


def reverse_geo(lat, lon):
    """
    Create short+full address string from given geo coordinates

    :return: Address named tuple
        short : string
            The "sort" Address
        full : string
            The "full" Address
    """
    lat2 = round(lat, ndigits=WGS84_NDIGITS)
    if lat2 != lat:
        log.debug(f'round lat={lat} -> {lat2}')

    lon2 = round(lon, ndigits=WGS84_NDIGITS)
    if lon2 != lon:
        log.debug(f'round lat={lon} -> {lon2}')

    log.debug(f'reverse_geo lat={lat2} lon={lon2}')

    cache_key = f'reverse_geo_{lat2}_{lon2}'
    log.debug('reverse geo cache key: %r', cache_key)
    address = cache.get(cache_key)
    if address:
        log.debug('reverse geo from cache')
        full_address, raw_address = address
    else:
        geolocator = Nominatim(user_agent="django-for-runners")

        # https://nominatim.org/release-docs/develop/api/Reverse/
        location = geolocator.reverse(
            query=f"{lat2}, {lon2}",
            # TODO: language={user language}
            zoom=17  # major and minor streets
        )
        full_address = location.address
        raw_address = location.raw["address"]
        address = (full_address, raw_address)
        log.debug('Store to cache: %r', cache_key)
        cache.set(
            cache_key, address,
            timeout=None  # cache forever
        )

    short_address = construct_short_address(address=raw_address)
    log.info(f'short_address={short_address}')

    return Address(short_address, full_address)


if __name__ == "__main__":
    print(reverse_geo("51.6239133", "6.9749074"))  # Bottrop Feldhausen
