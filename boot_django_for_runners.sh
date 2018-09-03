#!/usr/bin/env bash

"""
    Django-ForRunners boot script
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    More information in the README:

        https://github.com/jedie/django-for-runners#readme

    created 03.09.2018 by Jens Diemer <opensource@jensdiemer.de>
    :copyleft: 2018 by the django-for-runners team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

DESTINATION=~/Django-ForRunners
REPOSITORY="git+https://github.com/jedie/django-for-runners.git"
BRANCH="master"
EGG="django-for-runners"

(
    set -e
    set -x

    python3 --version
    python3 -Im venv --without-pip ${DESTINATION}
)
(
    source ${DESTINATION}/bin/activate
    set -x
    python3 -m ensurepip
)
if [ "$?" == "0" ]; then
    echo "pip installed, ok"
else
    echo "ensurepip doesn't exist, use get-pip.py"
    (
        set -e
        source ${DESTINATION}/bin/activate
        set -x
        cd ${DESTINATION}/bin
        wget https://bootstrap.pypa.io/get-pip.py
        ${DESTINATION}/bin/python get-pip.py
    )
fi
(
    set -e
    source ${DESTINATION}/bin/activate
    set -x
    cd ${DESTINATION}/bin/

    pip3 install --upgrade pip
    pip3 install -e ${REPOSITORY}@${BRANCH}#egg=${EGG}

    pip3 install -r ${DESTINATION}/src/django-for-runners/requirements.txt

    cd ${DESTINATION}/bin/
    ./for_runners --version
)
