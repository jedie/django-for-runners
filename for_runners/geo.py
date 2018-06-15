"""
    created 31.05.2018 by Jens Diemer <opensource@jensdiemer.de>
    :copyleft: 2018 by the django-for-runners team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""
import collections
import logging

from geopy.geocoders import Nominatim

log = logging.getLogger(__name__)
Address = collections.namedtuple('Address', ('short, full'))


def construct_short_address(address):
    # from pprint import pprint
    # pprint(address)
    parts = []

    if "village" in address and "county" in address:
        parts.append("%s," % address["village"])
        parts.append(address["county"])
    else:
        parts.append(address.get("city") or address.get("town") or address.get("county") or address.get("state"))
        parts.append(address.get("suburb"))

    short_address = " ".join([part for part in parts if part])
    return short_address


def reverse_geo(lat, lon):
    """
    Create short+full address string from given geo coordinates

    >>> address = reverse_geo("51.6239133", "6.9749074")
    >>> address.short
    'Feldhausen, Bottrop'
    >>> address.full
    'Studio 7, The Old West, Feldhausen, Bottrop, Regierungsbezirk Münster, Nordrhein-Westfalen, 46244, Deutschland'

    >>> reverse_geo("52.518611", "13.376111").short
    'Berlin Tiergarten'

    :return: Address named tuple
        short : string
            The "sort" Address
        full : string
            The "full" Address
    """
    geolocator = Nominatim()
    location = geolocator.reverse("%s, %s" % (lat, lon))

    short_address = construct_short_address(address=location.raw["address"])

    return Address(short_address, location.address)


if __name__ == "__main__":
    print(reverse_geo("51.6239133", "6.9749074")) # Bottrop Feldhausen
