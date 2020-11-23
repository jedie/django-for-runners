# https://hub.docker.com/_/python
FROM python:3.9-slim-buster

# for pip cache:
ENV XDG_CACHE_HOME=/var/cache

ENV PYTHONUNBUFFERED=1

# Install deps
RUN set -x \
    && apt-get update \
    && apt-mark auto $(apt-mark showinstall) \
    && apt-get install -y postgresql-client-11 python3-pip \
    && apt autoremove \
    && apt -y full-upgrade \
    && rm -rf /var/lib/apt \
    && python3 -m pip install -U pip \
    && pip install -U psycopg2-binary

# Create user for application server:
RUN set -x \
    && addgroup --system django \
    && adduser --system --no-create-home --disabled-password --ingroup django --shell /bin/bash django

WORKDIR /django

ARG PROJECT_PACKAGE_NAME
ENV PROJECT_PACKAGE_NAME=${PROJECT_PACKAGE_NAME}

ARG PROJECT_VERSION
ENV PROJECT_VERSION=${PROJECT_VERSION}

# Install project:
RUN set -x \
    && pip install "${PROJECT_PACKAGE_NAME}>=${PROJECT_VERSION}"


