#!/usr/bin/env bash

set -e

while true
do
(
    clear
    echo "====================================================================="
    set +e
    (
        set -x
        python3 ./manage.py run_test_project_dev_server $*
        sleep 2
    )
)
done
