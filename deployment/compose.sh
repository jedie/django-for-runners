#!/bin/bash

set -e

if [[ -f .env ]]; then
    echo "Read '.env' file..."
    source .env
fi

set -x

source project.env
exec poetry run docker-compose "$@"
