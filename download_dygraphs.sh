#!/usr/bin/env bash

#
# Update dygraphs (MIT License)
#
# http://dygraphs.com/
#

set -ex

mkdir -p for_runners/static/dygraph
cd for_runners/static/dygraph

#
# download link from:
# https://cdnjs.com/libraries/dygraph
#
wget --timestamp https://cdnjs.cloudflare.com/ajax/libs/dygraph/2.1.0/dygraph.css
wget --timestamp https://cdnjs.cloudflare.com/ajax/libs/dygraph/2.1.0/dygraph.min.css
wget --timestamp https://cdnjs.cloudflare.com/ajax/libs/dygraph/2.1.0/dygraph.min.css.map
wget --timestamp https://cdnjs.cloudflare.com/ajax/libs/dygraph/2.1.0/dygraph.js
wget --timestamp https://cdnjs.cloudflare.com/ajax/libs/dygraph/2.1.0/dygraph.min.js
wget --timestamp https://cdnjs.cloudflare.com/ajax/libs/dygraph/2.1.0/dygraph.min.js.map
