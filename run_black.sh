#!/usr/bin/env bash

source ../../bin/activate

set -ex

black --safe --line-length=119 for_runners for_runners_project for_runners_tests
