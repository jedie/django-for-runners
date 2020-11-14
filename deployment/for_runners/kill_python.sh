#!/bin/sh

set -ex

for pid in $(pidof python3); do kill $pid; done
