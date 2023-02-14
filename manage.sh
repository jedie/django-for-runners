#!/bin/sh

(
    set -x
    poetry run python --version
    poetry run django-admin --version
)

exec poetry run python3 manage.py "$@"
