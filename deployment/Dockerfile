FROM python:3.9-slim-buster
# https://hub.docker.com/_/python

ARG XDG_CACHE_HOME
ENV XDG_CACHE_HOME=${XDG_CACHE_HOME}

# Install deps
RUN apt-get update \
    && apt-mark auto $(apt-mark showinstall) \
    && apt-get install -y postgresql-client-11 python3-pip \
    && apt autoremove \
    && apt -y full-upgrade \
    && rm -rf /var/lib/apt \
    && python3 -m pip install -U pip \
    && pip install -U psycopg2-binary

WORKDIR /django

RUN pip install "django-for-runners>=0.11.0"


