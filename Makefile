SHELL := /bin/bash
MAX_LINE_LENGTH := 119
export DJANGO_SETTINGS_MODULE ?= for_runners_project.settings.local

all: help

help:
	@echo -e '_________________________________________________________________'
	@echo -e 'DjangoForRunners - *dev* Makefile\n'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z0-9 -]+:.*?## / {printf "\033[36m%-22s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

check-poetry:
	@if [[ "$(shell poetry --version 2>/dev/null)" == *"Poetry"* ]] ; \
	then \
		echo "Poetry found, ok." ; \
	else \
		echo 'Please install poetry first, with e.g.:' ; \
		echo 'make install-poetry' ; \
		exit 1 ; \
	fi

install-poetry:  ## install or update poetry
	pip3 install -U pip
	pip3 install -U poetry

install: check-poetry  ## install project via poetry
	poetry install

update: check-poetry ## update the sources and installation
	git fetch --all
	git pull origin main
	poetry run pip install -U pip
	poetry update

manage-update: ## Collectstatic + makemigration + migrate
	./manage.sh collectstatic --noinput
	./manage.sh makemigrations
	./manage.sh migrate


tox-listenvs: check-poetry ## List all tox test environments
	poetry run tox --listenvs

tox: check-poetry ## Run pytest via tox with all environments
	poetry run tox

tox-py36: check-poetry ## Run pytest via tox with *python v3.6*
	poetry run tox -e py36

tox-py37: check-poetry ## Run pytest via tox with *python v3.7*
	poetry run tox -e py37

tox-py38: check-poetry ## Run pytest via tox with *python v3.8*
	poetry run tox -e py38

pytest: check-poetry ## Run pytest
	DJANGO_SETTINGS_MODULE=for_runners_project.settings.tests poetry run pytest --workers auto --tests-per-worker 1

update-rst-readme: ## update README.rst from README.creole
	poetry run update_rst_readme

publish: ## Release new version to PyPi
	poetry run publish

run-dev-server:  ## Run the django dev server in endless loop.
	./manage.sh collectstatic --noinput --link
	./manage.sh migrate
	./manage.sh runserver

createsuperuser:  ## Create super user
	./manage.sh createsuperuser

messages: ## Make and compile locales message files
	./manage.sh makemessages --all --no-location --no-obsolete
	./manage.sh compilemessages

##############################################################################

dumpdata:  ## Backup database with Django's dumpdata
	./manage.sh dumpdata --indent 4 --exclude axes --exclude django_processinfo >dumpdata.json

##############################################################################

dbbackup:  ## Backup database
	./manage.sh dbbackup

dbrestore:  ## Restore a database backup
	./manage.sh dbrestore

##############################################################################

run-docker-dev-server:  ## Start docker containers with current dev source code
	rm -Rf dist/
	poetry build
	rm -Rf deployment/dist/
	cp -ruv dist deployment/
	cd deployment && make down
	cd deployment && ./compose.dev.sh build --pull
	cd deployment && ./compose.dev.sh up

shell_docker-dev-server:  ## Go into bash shell in for_runners container
	cd deployment && ./compose.dev.sh exec for_runners /bin/bash

##############################################################################

.PHONY: help install lint fix test publish