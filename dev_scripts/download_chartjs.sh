#!/usr/bin/env bash

#
# Update Leaflet
#

set -ex

cd ../for_runners/static/chartjs

#
# download link from:
# https://leafletjs.com/download.html
#
wget https://github.com/chartjs/Chart.js/releases/download/v2.7.2/Chart.bundle.min.js
