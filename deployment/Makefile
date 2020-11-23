SHELL := /bin/bash

all: help

help:
	@echo -e '_________________________________________________________________'
	@echo -e '*Deployment* Makefile\n'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z0-9 -_]+:.*?## / {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

check-poetry:
	@if [[ "$(shell poetry --version 2>/dev/null)" == *"Poetry"* ]] ; \
	then \
		echo "Poetry found, ok." ; \
	else \
		echo 'Please install poetry first, with e.g.:' ; \
		echo 'make install-poetry' ; \
		exit 1 ; \
	fi

install-poetry: ## install or update poetry
	@if [[ "$(shell poetry --version 2>/dev/null)" == *"Poetry"* ]] ; \
	then \
		echo 'Update poetry' ; \
		poetry self update ; \
	else \
		echo 'Install poetry' ; \
		curl -sSL "https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py" | python3 ; \
	fi

install: check-poetry ## install requirements to setup project
	poetry install

update: check-poetry ## update the sources and docker containers
	git fetch --all
	git pull origin master
	poetry update
	./compose.sh build --pull
	$(MAKE) restart

check-compose:
	@if [[ "$(shell poetry run docker-compose --version 2>/dev/null)" = *"docker-compose version"* ]] ; \
	then \
		echo "docker-compose found, ok." ; \
	else \
		echo 'Please install extras first, with e.g.:' ; \
		echo 'make install-compose' ; \
		exit 1 ; \
	fi

up: check-compose  ## Start containers via docker-compose
	./compose.sh up -d
	$(MAKE) prune
	./compose.sh logs --tail=500 --follow

down:  ## Stop all containers
	./compose.sh down

prune:  ## Cleanup docker
	docker system prune --force --all --filter until=4464h

build: check-compose  ## Update docker container build
	./compose.sh pull
	./compose.sh build --pull

init_postgres:  ## Create postgres database
	./compose.sh exec postgres ./docker/postgres_init.sh

##############################################################################

createsuperuser:  ## Create super user
	./compose.sh exec django ./manage.sh createsuperuser

##############################################################################

shell_django:  ## Go into bash shell in django container
	./compose.sh exec django /bin/bash

shell_postgres:  ## Go into bash shell in postgres container
	./compose.sh exec postgres /bin/bash

shell_caddy:  ## Go into bash shell in caddy container
	./compose.sh exec caddy /bin/ash

##############################################################################

caddy_environ:  ## Prints the caddy environment
	./compose.sh exec caddy /usr/bin/caddy environ

##############################################################################

logs:  ## Display docker logs from all containers
	./compose.sh logs --tail=500 --follow

logs_postgres:  ## Display docker logs from postgres container
	./compose.sh logs --tail=500 --follow postgres

logs_django:  ## Display docker logs from django container
	./compose.sh logs --tail=500 --follow django

logs_caddy:  ## Display docker logs from caddy container
	./compose.sh logs --tail=500 --follow caddy

##############################################################################

dbbackup:  ## Backup database
	./compose.sh exec django ./manage.sh dbbackup

dbrestore:  ## Restore a database backup
	./compose.sh exec django ./manage.sh dbrestore

##############################################################################

restart: down up  ## Restart all containers

upgrade_django:  ## Upgrade "django" container and restart it
	$(MAKE) build
	./compose.sh stop django
	$(MAKE) up

restart_caddy:  ## Restart caddy container
	./compose.sh stop caddy
	$(MAKE) up

##############################################################################

reload_caddy:  ## Reload Caddy server
	./compose.sh exec caddy caddy reload --config /etc/caddy/Caddyfile --adapter caddyfile
	$(MAKE) logs_caddy

reload_django:  ## Reload server in "django" container
	./compose.sh exec django /django/reload_gunicorn.sh
	./compose.sh logs --tail=500 --follow django

##############################################################################

.PHONY: help