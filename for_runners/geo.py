"""
    created 31.05.2018 by Jens Diemer <opensource@jensdiemer.de>
    :copyleft: 2018-2020 by the django-for-runners team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""
import collections
import logging

from geopy.geocoders import Nominatim


log = logging.getLogger(__name__)
Address = collections.namedtuple("Address", ("short, full"))


def construct_short_address(address):
    log.debug(f'address={address}')
    parts = []

    if "village" in address and "county" in address:
        parts.append(f"{address['village']},")
        parts.append(address["county"])
    else:
        parts.append(address.get("city") or address.get("town") or address.get("county") or address.get("state"))
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

    >>> address = reverse_geo("51.6239133", "6.9749074")
    >>> address.short
    'Feldhausen, Bottrop'
    >>> address.full[:70] + '...'
    'Movie Park Germany, 1, Warner-Allee, Kuhberg, Feldhausen, Bottrop, Nor...'

    >>> reverse_geo("52.518611", "13.376111").short
    'Berlin Tiergarten'

    :return: Address named tuple
        short : string
            The "sort" Address
        full : string
            The "full" Address
    """
    log.debug(f'reverse_geo lat={lat} lon={lon}')
    geolocator = Nominatim(user_agent="django-for-runners")
    location = geolocator.reverse(f"{lat}, {lon}")

    short_address = construct_short_address(address=location.raw["address"])
    log.info(f'short_address={short_address}')

    return Address(short_address, location.address)


if __name__ == "__main__":
    print(reverse_geo("51.6239133", "6.9749074"))  # Bottrop Feldhausen
