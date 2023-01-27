#!/bin/bash

./cli.py version

export DJANGO_SETTINGS_MODULE=for_runners_project.settings.local

exec .venv/bin/python3 manage.py "$@"
