#!/usr/bin/env bash

set -ex

git checkout master
git fetch --all
git pull origin master
git push origin master
