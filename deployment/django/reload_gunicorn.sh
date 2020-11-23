#!/bin/sh

set -ex

for pid in $(cat /tmp/gunicorn.pid); do kill $pid; done
