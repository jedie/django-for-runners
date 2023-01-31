SHELL := /bin/bash
MAX_LINE_LENGTH := 100
POETRY_VERSION := $(shell poetry --version 2>/dev/null)

help: ## List all commands
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z0-9 -]+:.*?## / {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

check-poetry:
	@if [[ "${POETRY_VERSION}" == *"Poetry"* ]] ; \
	then \
		echo "Found ${POETRY_VERSION}, ok." ; \
	else \
		echo 'Please install poetry first, with e.g.:' ; \
		echo 'make install-poetry' ; \
		exit 1 ; \
	fi

install-base-req: ## Install needed base packages via apt
	sudo apt install python3-pip python3-venv

install-poetry:  ## install or update poetry
	pip3 install -U pip
	pip3 install -U pipx
	pipx install poetry

install: check-poetry  ## install project via poetry
	python3 -m venv .venv
	poetry install

update: check-poetry ## update the sources and installation
	git fetch --all
	git pull origin main
	pip3 install -U pip
	pip3 install -U pipx
	pipx upgrade poetry
	poetry update

lint: ## Run code formatters and linter
	poetry run darker --diff --check
	poetry run flake8 .

fix-code-style: ## Fix code formatting
	poetry run darker
	poetry run flake8 .

tox-listenvs: check-poetry ## List all tox test environments
	poetry run tox --listenvs

tox: check-poetry ## Run pytest via tox with all environments
	poetry run tox

pytest: check-poetry  ## Run pytest
	poetry run python --version
	poetry run django-admin --version
	poetry run pytest

renew-fixtures: ## Renew all fixture files
	./manage.sh renew_fixtures

publish: ## Release new version to PyPi
	poetry run publish

run-dev-server: ## Run the django dev server in endless loop.
	./manage.sh run_dev_server

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

.PHONY: help install lint fix test publish