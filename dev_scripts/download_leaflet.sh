#!/usr/bin/env bash

#
# Update Leaflet
#

set -ex

cd ../for_runners/static/leaflet

#
# download link from:
# https://leafletjs.com/download.html
#
wget http://cdn.leafletjs.com/leaflet/v1.3.1/leaflet.zip

unzip -u leaflet.zip

rm leaflet.zip
