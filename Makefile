SHELL := /bin/bash

help: ## List all commands
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z0-9 -]+:.*?## / {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

renew-fixtures: ## Renew all fixture files
	./manage.sh renew_fixtures

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
