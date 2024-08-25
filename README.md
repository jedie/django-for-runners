# Django-ForRunners

![Logo](https://github.com/jedie/django-for-runners/raw/main/for_runners/static/Django-ForRunners128.png "Logo") Store your GPX tracks of your running (or other sports activity) in django.

[![tests](https://github.com/jedie/django-for-runners/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/jedie/django-for-runners/actions/workflows/tests.yml)
[![codecov](https://codecov.io/github/jedie/for_runners/branch/main/graph/badge.svg)](https://app.codecov.io/github/jedie/for_runners)
[![django-for-runners @ PyPi](https://img.shields.io/pypi/v/django-for-runners?label=django-for-runners%20%40%20PyPi)](https://pypi.org/project/django-for-runners/)
[![Python Versions](https://img.shields.io/pypi/pyversions/django-for-runners)](https://github.com/jedie/django-for-runners/blob/main/pyproject.toml)
[![License GPL-3.0-or-later](https://img.shields.io/pypi/l/django-for-runners)](https://github.com/jedie/django-for-runners/blob/main/LICENSE)

(The name **Django-ForRunners** has the origin from the great Android tracking app **ForRunners** by Benoît Hervier: [http://rvier.fr/#forrunners](http://rvier.fr/#forrunners) )

[![Install Django-ForRunners with YunoHost](https://install-app.yunohost.org/install-with-yunohost.svg)](https://install-app.yunohost.org/?app=django-for-runners_ynh)

> [django-for-runners_ynh](https://github.com/YunoHost-Apps/django-for-runners_ynh) allows you to install Django-ForRunners quickly and simply on a YunoHost server. If you don't have YunoHost, please consult [the guide](https://yunohost.org/#/install) to learn how to install it.

## Features:


* GPX track management:
  * Upload GPX tracks
  * Import GPX tracks from commandline
  * Track analysis:
    * basics: Track length / Duration / Pace / Hart rate Up-/Downhill
    * Display route on OpenStreetMap map
    * Graphs with elevation / heart rate / cadence (if available in GPX data)
  * Data that is automatically extracted from the web:
    * Start/finish Address from OpenStreetMap
    * Start/finish weather information from metaweather.com
  * Store additional data:
    * Ideal track distance (for easier grouping/filtering tracks)
* sports competitions Management:
  * Create a List of Sport Events
    * Add participation to a event
    * link GPX track with a event participation
    * Store you event participation:
      * official track length
      * measured finisher time
      * Number of participants who have finished in your discipline
    * Add links to webpages relatet to this event
    * Record costs (entry fee, T-shirt etc.)
* common
  * Multiple user support (However: no rights management and currently only suitable for a handful of users)


## Developer information

### prepare

To start hacking: Just clone the project and start `./manage.py` to bootstrap a virtual environment:

```bash
# Install base requirements for bootstraping:
~$ sudo apt install python3-pip python3-venv

# Get the sources:
~$ git clone https://github.com/jedie/django-for-runners.git
~$ cd django-for-runners/

# Just call manage.py:
~/django-for-runners$ ./manage.py --help
...
[manage_django_project]
    code_style
    coverage
    install
    project_info
    publish
    run_dev_server
    safety
    tox
    update_req
...
```
This bootstrap is realized with: https://github.com/jedie/manage_django_project



Start Django's dev server:
```bash
~/django-for-runners$ ./manage.py run_dev_server
````
The web page is available in Port 8000, e.g.: `http://127.0.0.1:8000/`


Run tests, e.g.:
```bash
~/django-for-runners$ ./manage.py test
# or with coverage
~/django-for-runners$ ./manage.py coverage
# or via tox:
~/django-for-runners$ ./manage.py tox
````



### import GPX files

e.g.:
```
~/django-for-runners$ ./manage.py import_gpx --username <django_username> ~/backups/gpx_files
```

**Note:** It is no problem to start **import_gpx** with the same GPX files: Duplicate entries are avoided. The start/finish (time/latitude/longitude) are compared.

### backup

Create a backup into `.../backups/<timestamp>/` e.g.:
```
~/django-for-runners$ ./manage.py backup
```

The backup does:


* backup the database
* export all GPX tracks
* generate .csv files:
* a complete file with all running tracks
* one file for every user



## Screenshots

(All screenshots are here: [github.com/jedie/jedie.github.io/tree/master/screenshots/django-for-runners](https://github.com/jedie/jedie.github.io/tree/master/screenshots/django-for-runners))

## for-runers v0.6.0 2018-07-31 GPX Track.png

![for-runers v0.6.0 2018-07-31 GPX Track.png](https://raw.githubusercontent.com/jedie/jedie.github.io/master/screenshots/django-for-runners/for-runers%20v0.6.0%202018-07-31%20GPX%20Track.png "for-runers v0.6.0 2018-07-31 GPX Track.png")

## for-runners v0.4.0 2018-6-26 GPX info.png

![for-runners v0.4.0 2018-6-26 GPX info.png](https://raw.githubusercontent.com/jedie/jedie.github.io/master/screenshots/django-for-runners/for-runners%20v0.4.0%202018-6-26%20GPX%20info.png "for-runners v0.4.0 2018-6-26 GPX info.png")

## for-runners v0.6.0 2018-07-19 Event Costs.png

![for-runners v0.6.0 2018-07-19 Event Costs.png](https://raw.githubusercontent.com/jedie/jedie.github.io/master/screenshots/django-for-runners/for-runners%20v0.6.0%202018-07-19%20Event%20Costs.png "for-runners v0.6.0 2018-07-19 Event Costs.png")

## print a small overview

![for-runners v0.10.0 2010-06-26 print small overview 1.png](https://raw.githubusercontent.com/jedie/jedie.github.io/master/screenshots/django-for-runners/for-runners%20v0.10.0%202010-06-26%20print%20small%20overview%201.png "for-runners v0.10.0 2010-06-26 print small overview 1.png")

![for-runners v0.10.0 2010-06-26 print small overview 2.png](https://raw.githubusercontent.com/jedie/jedie.github.io/master/screenshots/django-for-runners/for-runners%20v0.10.0%202010-06-26%20print%20small%20overview%202.png "for-runners v0.10.0 2010-06-26 print small overview 2.png")


## some notes

### GPX storage

Currently we store the unchanged GPX data in a TextField.

### static files

We collect some JavaScript files, for easier startup. These files are:

| Project Homepage                      | License                                                                                   | storage directory                                                                                                   |
| ------------------------------------- | ----------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| [leafletjs.com](http://leafletjs.com) | [Leaflet licensed under BSD](https://github.com/Leaflet/Leaflet/blob/master/LICENSE)      | [for_runners/static/leaflet/](https://github.com/jedie/django-for-runners/tree/master/for_runners/static/leaflet)   |
| [dygraphs.com](http://dygraphs.com)   | [dygraphs licensed under MIT](https://github.com/danvk/dygraphs/blob/master/LICENSE.txt)  | [for_runners/static/dygraphs/](https://github.com/jedie/django-for-runners/tree/master/for_runners/static/dygraphs) |
| [chartjs.org](http://www.chartjs.org) | [Chart.js licensed under MIT](https://github.com/chartjs/Chart.js/blob/master/LICENSE.md) | [for_runners/static/chartjs/](https://github.com/jedie/django-for-runners/tree/master/for_runners/static/chartjs)   |

### Precision of coordinates

GPX files from Garmin (can) contain:


* latitude with 29 decimal places
* longitude with 28 decimal places
* elevation with 19 decimal places

The route on OpenStreetMap does not look more detailed, with more than 5 decimal places.

See also: [https://wiki.openstreetmap.org/wiki/Precision_of_coordinates](https://wiki.openstreetmap.org/wiki/Precision_of_coordinates)


## Make new release

We use [cli-base-utilities](https://github.com/jedie/cli-base-utilities#generate-project-history-base-on-git-commitstags) to generate the history in this README.


To make a new release, do this:

* Increase your project version number
* Run tests to update the README
* commit the changes
* Create release


## Django compatibility

| django-for-runners | django version | python              |
|--------------------|----------------|---------------------|
| >=v0.20.0          | 5.1            | 3.11, 3.12          |
| >=v0.16.0          | 4.1            | 3.9, 3.10, 3.11     |
| >=v0.15.0          | 3.2, 4.0, 4.1  | 3.7, 3.8, 3.9, 3.10 |
| >=v0.14.0          | 3.2            | 3.7, 3.8, 3.9, 3.10 |
| >=v0.12.0          | 2.2            | 3.7, 3.8, 3.9, 3.10 |
| >=v0.11.0          | 2.2            | 3.7, 3.8, 3.9       |
| >=v0.7.1           | 2.1            | 3.5, 3.6, 3.7       |
| v0.5.x             | 2.0            | 3.5, 3.6, 3.7       |

(See also combinations in [tox settings in pyproject.toml](https://github.com/jedie/django-for-runners/blob/main/pyproject.toml) and [github actions](https://github.com/jedie/django-for-runners/blob/main/.github/workflows/tests.yml))


## Backwards-incompatible changes


### v0.16.0

We switched from Poetry to pip-tools and https://github.com/jedie/manage_django_project
Just remove the old Poetry venv and bootstrap by call the `./manage.py`, see above.

We also remove different Django Versions from test matrix and just use the current newest version.
Because this is a project and not really a reuse-able-app ;)




## history


[comment]: <> (✂✂✂ auto generated history start ✂✂✂)

* [v0.20.0](https://github.com/jedie/django-for-runners/compare/v0.19.0...v0.20.0)
  * 2024-08-25 - Update requirements
  * 2024-08-25 - Apply manageprojects updates
  * 2024-08-13 - Bugfix broken event change list, if no events exists
  * 2024-08-13 - Allow facets in GPX change list
  * 2024-08-13 - Dump Version
  * 2024-08-13 - Update README
  * 2024-08-13 - Update to Django 5.1
* [v0.19.0](https://github.com/jedie/django-for-runners/compare/v0.18.1...v0.19.0)
  * 2024-08-04 - Relase as v0.19.0
  * 2024-08-04 - bugfix 3.11 installation
  * 2024-08-04 - Fix Code style
  * 2024-08-04 - Enhance tracks upload in change list:
  * 2024-08-04 - Set min. Python v3.11
  * 2024-08-04 - update requirements
* [v0.18.1](https://github.com/jedie/django-for-runners/compare/v0.18.0...v0.18.1)
  * 2024-08-02 - Update/fix "fill_basedata" command
* [v0.18.0](https://github.com/jedie/django-for-runners/compare/v0.17.4...v0.18.0)
  * 2024-08-02 - Update README.md
  * 2024-08-02 - Expand test matrix with 3.12 and remove 3.9 support
  * 2024-08-02 - Bugfix CI: Add "*.snapshot.json" files ;)
  * 2024-08-02 - Add https://pre-commit.com hook
  * 2024-08-02 - Replace "safety" by "pip-audit"
  * 2024-08-01 - Replace metaweather.com with open-meteo.com
  * 2024-08-01 - Update test_add_gpx()
  * 2024-08-01 - Update Leaflet to v1.9.4 and fix styles
  * 2024-08-01 - Support KML track import created by Pentax K-1
  * 2024-08-01 - Catch metaweather.com error
  * 2024-07-31 - Project updates
  * 2024-07-31 - Update requirements
  * 2024-01-18 - +typeguard +manageprojects updates
  * 2023-12-17 - Use cli_base.cli_tools.git_history.update_readme_history()
  * 2023-12-17 - Update requirements ; TODO: Update to Django 5.0
  * 2023-12-17 - Code style fixes
  * 2023-12-17 - Apply manageprojects updates

<details><summary>Expand older history entries ...</summary>

* [v0.17.4](https://github.com/jedie/django-for-runners/compare/v0.17.3...v0.17.4)
  * 2023-11-07 - audo generate README history
  * 2023-11-07 - Update Requirements
  * 2023-11-07 - Update UploadGpxFileForm
  * 2023-04-05 - Update to manage-django-project v0.3.0rc0
  * 2023-04-05 - Bugfixes:
  * 2023-04-04 - Switch to "managed-django-project" template:
* [v0.17.3](https://github.com/jedie/django-for-runners/compare/v0.17.2...v0.17.3)
  * 2023-04-03 - Bugfix check if Postgres is used and migration not done
* [v0.17.2](https://github.com/jedie/django-for-runners/compare/v0.17.1...v0.17.2)
  * 2023-04-02 - release 0.17.2
  * 2023-04-02 - Bugfix adding all template files
* [v0.17.1](https://github.com/jedie/django-for-runners/compare/v0.17.0...v0.17.1)
  * 2023-04-02 - Bugfix packaging and missing files
  * 2023-04-02 - update link to https://github.com/kbr/autotask
* [v0.17.0](https://github.com/jedie/django-for-runners/compare/v0.16.0...v0.17.0)
  * 2023-04-02 - Bugfix edit a `GpxModel` instance in admin with a large GPX track
  * 2023-04-02 - Bugfix manage call and merge project test code
  * 2023-04-02 - update ProjectSetupTestCase
  * 2023-04-02 - fix code style
  * 2023-04-02 - Update requirements
  * 2023-04-02 - apply manages projects
  * 2023-04-02 - -prod_settings
  * 2023-04-02 - update project
* [v0.16.0](https://github.com/jedie/django-for-runners/compare/v0.15.0...v0.16.0)
  * 2023-03-13 - update requirements
  * 2023-03-12 - code cleanup: Remove obsolete file
  * 2023-03-12 - Code cleanup around init
  * 2023-03-12 - Use https://github.com/jedie/manage_django_project
  * 2023-03-11 - Update README.md
  * 2023-01-27 - poetry -> piptools
  * 2023-02-07 - manageprojects
  * 2023-01-31 - use .venv, update req
  * 2022-08-30 - check_editor_config
  * 2022-08-30 - NEW: Attach files and images to "Event Participations
  * 2022-08-30 - Rename model field participation person to user
* [v0.15.0](https://github.com/jedie/django-for-runners/compare/v0.14.0...v0.15.0)
  * 2022-08-29 - bugfix publishing
  * 2022-08-29 - update README
  * 2022-08-29 - Use 'for_runners_project.settings.local' as default
  * 2022-08-29 - Bugfix run_dev_server command
  * 2022-08-23 - WIP: Replace README.creole with README.md
  * 2022-08-17 - Bugfix test settings
  * 2022-08-17 - add info
  * 2022-08-17 - bugfix "make update-rst-readme"
  * 2022-08-17 - Use AlwaysLoggedInAsSuperUserMiddleware from django-tools for local dev. server
  * 2022-08-17 - Use django_tools.management.commands.run_testserver
  * 2022-08-17 - update requirements
  * 2022-08-17 - update poetry, too
  * 2022-08-16 - Speedup CI
  * 2022-08-16 - tox: run with multiple django versions
* [v0.14.0](https://github.com/jedie/django-for-runners/compare/v0.13.0...v0.14.0)
  * 2022-08-16 - +"make lint"
  * 2022-08-16 - Update to Django 3.2
  * 2022-08-16 - fix editorconfig
  * 2022-08-16 - uses: codecov/codecov-action@v2
  * 2022-07-06 - Bump lxml from 4.8.0 to 4.9.1
  * 2022-06-02 - Bump pillow from 9.1.0 to 9.1.1
  * 2022-04-16 - Bugfix backup
* [v0.13.0](https://github.com/jedie/django-for-runners/compare/v0.12.1...v0.13.0)
  * 2022-04-15 - v0.13.0rc1
  * 2022-04-15 - Refresh all metaweather/OSM fixtures and use tooling from bx_django_utils
  * 2022-04-15 - Fix Tests by addning ignored .json fixture files
  * 2022-04-15 - fix coverage report
  * 2022-04-15 - fix darker in github actions
  * 2022-04-15 - set v0.13.0
  * 2022-04-15 - fix styles/tests
  * 2022-04-15 - Remove "/development/" and mode "/src/"
  * 2022-04-15 - fix tox config
  * 2022-04-15 - fix code style
  * 2022-04-15 - use darker
  * 2022-04-15 - Update Project setup
  * 2022-04-15 - master -> main
  * 2022-04-15 - Update requirements
  * 2022-03-12 - Bump pillow from 9.0.0 to 9.0.1
  * 2022-02-10 - Bump django from 2.2.26 to 2.2.27
  * 2022-01-13 - Bump django from 2.2.25 to 2.2.26
  * 2022-01-13 - Bump pillow from 8.4.0 to 9.0.0
  * 2021-12-15 - Bump django from 2.2.24 to 2.2.25
  * 2021-12-13 - Bump lxml from 4.6.4 to 4.6.5
* [v0.12.1](https://github.com/jedie/django-for-runners/compare/v0.12.0...v0.12.1)
  * 2021-11-22 - fix readme
  * 2021-11-22 - Update pythonapp.yml
  * 2021-11-22 - update requirements
  * 2021-11-22 - cleanup gitignore
  * 2021-11-22 - update github actions
  * 2021-05-23 - Update Github CI config
  * 2021-05-23 - Code cleanup
  * 2021-05-23 - remove Travis CI config
  * 2021-05-23 - Update requirements + code changes for bx_py_utils -> bx_django_utils
* [v0.12.0](https://github.com/jedie/django-for-runners/compare/v0.11.0...v0.12.0)
  * 2021-01-17 - prepare v0.12.0 release
  * 2021-01-17 - update README
  * 2021-01-17 - Link to django-for-runners_ynh in README
  * 2021-01-17 - fix logo in README
  * 2021-01-17 - update badge in README
  * 2021-01-17 - fix GPX file upload test
  * 2021-01-17 - update deps
  * 2020-12-30 - update tests
  * 2020-12-30 - update requirements
  * 2020-12-30 - set version to 0.12.0.rc3
  * 2020-12-30 - remove colorama and cleanup
  * 2020-12-30 - update to latest bx_py_utils
  * 2020-12-30 - install poetry via pip and update pip in venv, too
  * 2020-11-25 - Fix code style
  * 2020-11-25 - Add view to serve MEDIA files only for allowed user
  * 2020-11-25 - print to stderr (so it's not in the dumpdata ;)
  * 2020-11-25 - Add "adminer" container to dev run
  * 2020-11-25 - add "make dumpdata"
  * 2020-11-25 - fix project setup
  * 2020-11-24 - fix "make fix-code-style"
  * 2020-11-24 - fix coverage
  * 2020-11-24 - Bugfix "make pytest" by using the test settings
  * 2020-11-24 - check if cache is working in tests
  * 2020-11-24 - use LocMemCache as default cache backend
  * 2020-11-24 - geo reverse test: check if cache is filles
  * 2020-11-24 - Add one missing request mock in tests
  * 2020-11-24 - Activate "pytest-randomly"
  * 2020-11-24 - Mock HTTP-Requests and django file storage in tests
  * 2020-11-23 - migrate deployment setup from PyInventory
  * 2020-11-23 - Fix test
  * 2020-11-23 - Work a round for created static/media files in tests
  * 2020-11-23 - Mock some nominatim.openstreetmap.org requests in tests
  * 2020-11-14 - mock geo() request against "nominatim.openstreetmap.org/reverse"
  * 2020-11-14 - Remove django-tools API change warnings
  * 2020-11-14 - Don't use pytest-parallel on CI
  * 2020-11-14 - add "pytest-parallel"
  * 2020-11-14 - try to fix github actions
  * 2020-11-14 - try optimize github action?
  * 2020-11-14 - fix tox selenium tests by "passenv = *"
  * 2020-11-14 - fix setup
  * 2020-11-14 - WIP: fix docker setup
  * 2020-11-14 - add github actions
  * 2020-11-14 - set versions number to 0.12.0.rc1
  * 2020-11-14 - Add deployment stuff
  * 2020-11-14 - WIP: Update project setup
  * 2020-11-14 - add manage files
  * 2020-11-14 - update Makefile
  * 2020-11-14 - WIP: update django project
  * 2020-11-14 - remove git_sync.sh
  * 2020-11-14 - move to /src/
  * 2020-11-14 - +dev_scripts/fill_translations.py
  * 2020-11-14 - update project meta files
* [v0.11.0](https://github.com/jedie/django-for-runners/compare/v0.10.1...v0.11.0)
  * 2020-07-04 - Update README
  * 2020-07-04 - move download scripts into /dev_scripts/
  * 2020-07-04 - fix code styles
  * 2020-07-04 - add .flake8 config file
  * 2020-07-04 - Update requirements
  * 2020-07-04 - Add "make update"
  * 2020-06-09 - apply pyupgrade
  * 2020-06-09 - +pyupgrade
  * 2020-06-09 - apply autopep8
  * 2020-06-09 - setup autopep8 in pyproject.toml
  * 2020-06-09 - Apply isort
  * 2020-06-09 - add isort config file
  * 2020-06-09 - apply flynt
  * 2020-06-09 - Fix SVG test by compare it via parsed DOM-Tree ;)
  * 2020-06-06 - remove double elements in short-address
  * 2020-06-06 - disable pytest "randomly" plugin by default
  * 2020-06-06 - remove obsolete "update" cli command
  * 2020-06-06 - deactivate test TODO: Update it
  * 2020-06-06 - remove obsolete test
  * 2020-06-06 - fix for_runners/tests/test_svg.py
  * 2020-06-06 - update doctest in geo.py and add logging output
  * 2020-06-06 - Use poetry and a make file
  * 2020-06-09 - Update base.txt
  * 2020-06-06 - update gunicorn server
  * 2020-06-06 - Bugfix 'fill_basedata' manage command
  * 2019-08-25 - WIP: update tests
  * 2019-08-25 - Add a hint on UnicodeEncodeError in own manage commands
  * 2019-08-25 - refactor gpx import code and tests
  * 2019-08-25 - add link to: https://github.com/rsjrny/Garmin-Connect-Export
  * 2019-08-25 - remove link to gpsies.com
* [v0.10.1](https://github.com/jedie/django-for-runners/compare/v0.10.0...v0.10.1)
  * 2019-08-09 - Update .travis.yml
  * 2019-08-09 - list_display_links = ("event_name",)
  * 2019-06-26 - Add start date and costs to "Event Participation" table
* [v0.10.0](https://github.com/jedie/django-for-runners/compare/v0.9.0...v0.10.0)
  * 2019-06-26 - update README
  * 2019-04-08 - tweak print view
  * 2019-04-08 - generate missing svg files
  * 2019-04-08 - Bugfix generate_svg
  * 2019-04-08 - NEW: print mini
  * 2019-04-03 - fixup! fix test
  * 2019-04-03 - only code cleanup
  * 2019-04-03 - add date filter on gpx tracks
  * 2019-04-03 - fix test
  * 2019-04-03 - Accept optional server bind address
  * 2019-04-03 - pip for python 3 is needed for boot
* [v0.9.0](https://github.com/jedie/django-for-runners/compare/v0.8.1...v0.9.0)
  * 2019-04-02 - fixup! skip after_install_callback() on "publish"
  * 2019-04-02 - only code formatting
  * 2019-04-02 - skip after_install_callback() on "publish"
  * 2019-04-02 - WIP: fix tests on python 3.5
  * 2019-04-02 - refactor SVG and GPX files
  * 2019-04-02 - update tests
  * 2019-04-02 - use cutted b32encode sha512 hash
  * 2019-04-02 - update tests for "add" -> "upload" redirect
  * 2019-04-02 - USE_TZ = True
  * 2019-04-02 - "run-gunicorn" -> "run-server"
  * 2019-04-02 - redirect the defaul add view to upload form view
  * 2019-04-02 - Bugfix: Ensure that there are no more than 2 decimal places
  * 2019-04-01 - use django_tools.file_storage.file_system_storage.OverwriteFileSystemStorage
  * 2019-04-01 - use colorlog
  * 2019-04-01 - use django_tools.exception_plus
  * 2019-04-01 - call self.full_clean() in save()
  * 2019-04-01 - bugfix "bin/for_runners update"
  * 2019-03-21 - WIP
  * 2019-03-21 - +** NEW: export GPX Data via {{{django-import-export}}}
  * 2019-03-21 - chmod +x
  * 2019-03-21 - just run black code formatting
  * 2019-03-21 - +run_black.sh
  * 2019-01-31 - fixup! update tests
  * 2019-01-31 - +test "for_runers update" command
  * 2019-01-31 - fix --version and test ;)
  * 2019-01-31 - print("Start up...")
  * 2019-01-31 - hack: use "run-gunicorn" as default action
  * 2019-01-31 - NEW: Update installation with: {{{for_runners update}}}
  * 2018-12-17 - remove admin action "export as json"
  * 2018-12-17 - cleanup export stuff
  * 2018-12-17 - create normal and dev.server starter
  * 2018-12-11 - nicer export
  * 2018-12-11 - remove debug prints
  * 2018-12-11 - +Andreas Hudzieczek
  * 2018-12-11 - use gunicorn as default
  * 2018-12-11 - +gunicorn
  * 2018-12-11 - WIP: django-import-export
  * 2018-11-18 - only code style
  * 2018-11-18 - add gunicorn as requirements
  * 2018-11-18 - supported running gunicorn server
  * 2018-11-18 - README
  * 2018-11-18 - finish backup/export
  * 2018-11-18 - WIP: export .csv files on backup
  * 2018-11-18 - +for_runners_project
  * 2018-11-18 - update click to v7.0
  * 2018-11-17 - WIP: Backup/export via cli: "$ for_runners backup"
  * 2018-11-17 - move virtualenv path helper
  * 2018-11-17 - refactor call manage command
  * 2018-11-17 - DjangoForRunnersEnv -> Django-ForRunners
  * 2018-11-17 - regenerate all SVG files by: "$ for_runners recreate_svg"
  * 2018-11-17 - remove " && bash -i" from desktop file
  * 2018-11-17 - +start by hand
  * 2018-09-16 - setup event admin change list
  * 2018-09-16 - Bugfix: Open browser only one time
  * 2018-09-15 - Create xdg-open desktop starter under linux
  * 2018-09-12 - +Windows
  * 2018-09-12 - Patches for windows usage
  * 2018-09-12 - Work-a-round for windows
  * 2018-09-12 - Create boot_django_for_runners.cmd
  * 2018-09-09 - add icon link in html head
  * 2018-09-09 - Update README.creole
  * 2018-09-09 - Add logo as 128x128 png
  * 2018-09-09 - Add logo as SVG
  * 2018-09-09 - fix tests for python 3.5
  * 2018-09-07 - update README
  * 2018-09-07 - refactory startup and rename "for_runners_test_project" -> "for_runners_project"
* [v0.8.1](https://github.com/jedie/django-for-runners/compare/v0.8.0...v0.8.1)
  * 2018-09-03 - v0.8.1
  * 2018-09-03 - bin/run_dev_server -> bin/for_runners
* [v0.8.0](https://github.com/jedie/django-for-runners/compare/v0.7.1...v0.8.0)
  * 2018-09-03 - v0.8 and README
  * 2018-09-03 - use pip cache from travis
  * 2018-09-03 - https://github.com/travis-ci/travis-ci/issues/8589#issuecomment-372947199
  * 2018-09-03 - +test boot script
  * 2018-09-03 - WIP: boot/setup/usage
  * 2018-09-03 - Update README.creole
  * 2018-09-03 - auto call 'fill_basedata'
  * 2018-09-03 - nicer error if django can't import
  * 2018-09-02 - Add links from event participation to GPX tracks
  * 2018-09-02 - GpxModel.participation ForeignKey->OneToOneField
* [v0.7.1](https://github.com/jedie/django-for-runners/compare/v0.7.0...v0.7.1)
  * 2018-09-02 - fix tests test with django 2.1
  * 2018-09-02 - fixup! fix staff user tests
  * 2018-09-02 - fix staff user tests
  * 2018-09-02 - Update README.creole
* [v0.7.0](https://github.com/jedie/django-for-runners/compare/v0.6.0...v0.7.0)
  * 2018-09-02 - update readme
  * 2018-09-02 - +AUTHORS
  * 2018-09-02 - fix #2
  * 2018-08-31 - move manipluation of list_display and list_filter
  * 2018-08-28 - update tests
  * 2018-08-28 - Add TODO
  * 2018-08-28 - handle ZeroDivisionError calculating pace
  * 2018-08-28 - redirect to change view after upload
  * 2018-08-21 - catch NotImplementedError and NotSupportedError for missing sqlite distinct feature
  * 2018-08-21 - install pytest version compatible with pytest-django
  * 2018-08-21 - update tests: OSM data changed
  * 2018-08-21 - WIP: Add links from gpx tracks to other admin change view
  * 2018-08-21 - Add username to headline
  * 2018-08-21 - display user names only if there are tracks from more than one user
  * 2018-08-21 - handle invalid GPX data while importing
  * 2018-08-21 - Replace "Change GPX Track" headline with more informations
  * 2018-08-21 - refactor route/graphs creation and style
  * 2018-08-21 - Bugfix admin filter "By has event": Update since model refactoring
  * 2018-08-21 - Bugfix admin filter "By has net duration": Update since model refactoring
  * 2018-07-31 - Update README.creole
  * 2018-07-31 - update screenshot
  * 2018-07-31 - refactor duration field
  * 2018-07-31 - for_runners/static/{dygraph => dygraphs}/
  * 2018-07-31 - cleanup
  * 2018-07-24 - replace gxp track chart.js with dygraph
  * 2018-07-19 - add link to all screenshots
  * 2018-07-19 - +for-runners v0.6.0 2018-07-19 Event Costs.png
* [v0.6.0](https://github.com/jedie/django-for-runners/compare/v0.5.0...v0.6.0)
  * 2018-07-19 - release v0.6
  * 2018-07-19 - tune event statistics
  * 2018-07-19 - Add some basic event statistics
  * 2018-07-19 - help text
  * 2018-07-19 - +CostModel
  * 2018-07-19 - split admin.py
  * 2018-07-19 - bugfix change event view
  * 2018-07-12 - WIP: event participation
* [v0.5.0](https://github.com/jedie/django-for-runners/compare/v0.4.0...v0.5.0)
  * 2018-07-04 - ignore pypy3 tests, because of "decimal.InvalidOperation"
  * 2018-07-04 - install via pypi
  * 2018-07-04 - +DocString
  * 2018-07-04 - +docutils
  * 2018-07-04 - update README
  * 2018-07-04 - WIP: fix travis
  * 2018-07-04 - update travis config
  * 2018-07-04 - update tox.ini
  * 2018-07-04 - recreate migrations
  * 2018-07-04 - fix length and duration in chartjs
  * 2018-07-04 - update to change OSM data
  * 2018-07-04 - code cleanup
  * 2018-07-04 - add a AppConfig
  * 2018-07-04 - remove autotask
  * 2018-07-04 - FIXME: https://bitbucket.org/kbr/autotask/pull-requests/3/
  * 2018-07-04 - Add http://editorconfig.org config file with isort config
  * 2018-07-04 - django-tools>=0.40.2
  * 2018-07-03 - remove old migrations
  * 2018-07-03 - update squashed migrations
  * 2018-07-03 - squash migrations
  * 2018-07-03 - store gpx in TextField and update svg save
  * 2018-07-03 - update tests for django 2.0
  * 2018-07-03 - update test references for gpxpy v1.3.2 see:
  * 2018-07-03 - WIP
  * 2018-07-02 - Add 'has GPX tracks' filter to Event
  * 2018-06-28 - change event model: "start_time" -> "start_date"
  * 2018-06-28 - Add "has event" filter
  * 2018-06-28 - remove double entry
  * 2018-06-28 - nicer length/duration in change list
  * 2018-06-28 - Add YAPF config file
  * 2018-06-28 - add change list filter 'has net duration'
  * 2018-06-28 - +!/.travis.yml
  * 2018-06-28 - $ ./manage.py fill_basedata
  * 2018-06-28 - split models.py
  * 2018-06-28 - Add 'net duration' field, for the officially measured time and use it for calculations if available.
  * 2018-06-28 - Don't generate SVG if it's already done in the past.
  * 2018-06-28 - Don't request address if start/finish address already set
  * 2018-06-28 - bugfix human_duration() DocTests
  * 2018-06-28 - change event number to positiv integer
  * 2018-06-28 - make event links optional
  * 2018-06-28 - bugfix "GPX info" table
  * 2018-06-28 - DATA_UPLOAD_MAX_MEMORY_SIZE = 5000000
  * 2018-06-27 - Add "ideal distances"
  * 2018-06-27 - bugfix get weather
  * 2018-06-27 - Bugfix change view: remove obsolete code
  * 2018-06-27 - remove obsolete code
  * 2018-06-27 - speedup by deactivating some django debug toolbar panels
* [v0.4.0](https://github.com/jedie/django-for-runners/compare/v0.3.0...v0.4.0)
  * 2018-06-26 - update screenshots + version: v0.4.0
  * 2018-06-26 - remove Streetmap image generated via geotiler
  * 2018-06-26 - enable bezier curves
  * 2018-06-26 - Nicer track map with kilometer points
  * 2018-06-26 - change Statistics links in filter section
  * 2018-06-26 - code style
  * 2018-06-26 - Add 'creator' to every track and use it as changelist filter
  * 2018-06-26 - NEW: Display GPX metadata
  * 2018-06-26 - Speedup by using a cache for gpxpy instances
  * 2018-06-26 - Add links to github/PyPi in admin footer
  * 2018-06-26 - NEW: "GPX Info"
  * 2018-06-26 - Bugfix upload GPX files: set user
  * 2018-06-26 - Skip weather if date is None
  * 2018-06-25 - combine track filters with statistic views
  * 2018-06-25 - display min/avg/max pace in distance statistics
* [v0.3.0](https://github.com/jedie/django-for-runners/compare/v0.2.0...v0.3.0)
  * 2018-06-23 - fixup! README
  * 2018-06-23 - README
  * 2018-06-23 - Update tests for change admin title
  * 2018-06-23 - better info on import with existing tracks
  * 2018-06-23 - +for-runners v0.3.0 2018-6-23 Distance Statistics.png
  * 2018-06-23 - fixup! handle if no weather data is available
  * 2018-06-23 - expand user path
  * 2018-06-23 - code style
  * 2018-06-23 - handle if no weather data is available
  * 2018-06-23 - add distance statistics
  * 2018-06-23 - Change django title/branding
  * 2018-06-23 - add weather information from metaweather.com
  * 2018-06-23 - description='Store your GPX tracks of your running (or other sports activity) in django.'
* [v0.2.0](https://github.com/jedie/django-for-runners/compare/v0.1.1...v0.2.0)
  * 2018-06-21 - Update README.creole
  * 2018-06-21 - Squashed commit of the following:
  * 2018-06-17 - Add static files (Charts.JS + Leaflet)
* [v0.1.1](https://github.com/jedie/django-for-runners/compare/v0.1.0...v0.1.1)
  * 2018-06-15 - release v0.1.1
  * 2018-06-15 - update screnshots
  * 2018-06-15 - add tests for gpx2svg - TODO: Use correct WGS 84 calculations
  * 2018-06-15 - Don't use {{ forloop.counter }} for kilometers in leaflet map
  * 2018-06-15 - Bugfix short_address if town is == "state"
  * 2018-06-15 - +list_filter: tracked_by
  * 2018-06-15 - add tests for create GPX in admin
  * 2018-06-15 - bugfix if GPX extension doesn't exists
  * 2018-06-15 - Bugfix creating GPX entry in admin
* [v0.1.0](https://github.com/jedie/django-for-runners/compare/v0.0.4...v0.1.0)
  * 2018-06-15 - move svg to collapse section
  * 2018-06-15 - cleanup popup
  * 2018-06-14 - typo
  * 2018-06-14 - Display every km on map
  * 2018-06-14 - Render interactive OpenStreetMap track map with Leaflet JS
  * 2018-06-14 - +== run tests
  * 2018-06-14 - setup selenium tests
  * 2018-06-13 - Don't check content type
  * 2018-06-13 - start/finish links to openstreetmap
  * 2018-06-12 - use a better filename for the map
  * 2018-06-12 - code cleanup
  * 2018-06-12 - nicer admin change list view
  * 2018-06-12 - sort length, duration & pace in admin
  * 2018-06-12 - Add DocTests
  * 2018-06-12 - print -> logging
  * 2018-06-12 - Display hours, too + DocTests
* [v0.0.4](https://github.com/jedie/django-for-runners/compare/v0.0.3...v0.0.4)
  * 2018-06-12 - Gpxity currently not used
  * 2018-06-12 - +== credits ==
  * 2018-06-12 - skip geotiler if SyntaxError while import, see also:
  * 2018-06-12 - Update README.creole
  * 2018-06-12 - Geotiler needs Python 3.6 or later
  * 2018-06-12 - Better Links to events
  * 2018-06-12 - TODO: Use UTC and handle time zone
  * 2018-06-12 - activate MAP_DOWNLOAD by default
  * 2018-06-12 - gpxpy #117 is implemented, but not release on PyPi, see:
  * 2018-06-12 - GPX error handling + tests
  * 2018-06-12 - run for_runners tests, too
  * 2018-06-12 - typo
* [v0.0.3](https://github.com/jedie/django-for-runners/compare/v0.0.2...v0.0.3)
  * 2018-06-12 - Use autotask to generate map in background
  * 2018-06-12 - create new figure for map
  * 2018-06-05 - +import GPX files
  * 2018-06-05 - +.gitignore
  * 2018-06-05 - +== try-out
  * 2018-06-05 - Use last TLS version
  * 2018-06-02 - min/average/max heart rate
  * 2018-06-02 - use gpxpy 'ns-namespace' branch to fix: https://github.com/tkrajina/gpxpy/issues/117
  * 2018-06-02 - redirect to /admin/for_runners/gpxmodel/
* [v0.0.2](https://github.com/jedie/django-for-runners/compare/v0.0.1...v0.0.2)
  * 2018-05-31 - generate SVG from track
  * 2018-05-31 - v0.0.2
  * 2018-05-30 - +git_sync.sh
  * 2018-05-30 - remove tests with django cms 3.4
  * 2018-05-30 - code cleanup
  * 2018-05-30 - update requirements
  * 2018-05-30 - remove django-meta
  * 2018-05-30 - remove unused templates
  * 2018-05-30 - Update README.creole
* [v0.0.1](https://github.com/jedie/django-for-runners/compare/6e05957...v0.0.1)
  * 2018-05-30 - add first code version
  * 2018-05-29 - Initial commit

</details>


[comment]: <> (✂✂✂ auto generated history end ✂✂✂)


## links

* Homepage: [http://github.com/jedie/django-for-runners](http://github.com/jedie/django-for-runners)
* PyPi: [https://pypi.org/project/django-for-runners/](https://pypi.org/project/django-for-runners/)

### activity exporter

It's sometimes hard to find a working project for exporting activities.
So here tools that i use currently:


* [Garmin-Connect-Export](https://github.com/rsjrny/Garmin-Connect-Export) from rsjrny

### alternatives (OpenSource only)


* [https://github.com/pytrainer/pytrainer](https://github.com/pytrainer/pytrainer) (Desktop Program)
* [https://github.com/GoldenCheetah/GoldenCheetah/](https://github.com/GoldenCheetah/GoldenCheetah/) (Desktop Program)

Online tools:


* [https://www.j-berkemeier.de/ShowGPX.html](https://www.j-berkemeier.de/ShowGPX.html) (de)

## credits

The whole thing is based on many excellent projects. Especially the following:


* [gpxpy](https://pypi.org/project/gpxpy/) GPX file parser
* [Leaflet JS](https://leafletjs.com) A JS library for interactive maps used to render the track on [OpenStreetMap](https://openstreetmap.org/)
* [dygraphs](http://dygraphs.com) open source JavaScript charting library
* [Chart.js](https://www.chartjs.org) HTML5 Charts
* [geopy](https://pypi.org/project/geopy/) Get geo location names of the GPX track start/end point
* [matplotlib](https://pypi.org/project/matplotlib/) plotting 2D graphics
* [autotask](https://pypi.org/project/autotask/) schedule background jobs
* [svgwrite](https://pypi.org/project/svgwrite/) Generating SVG file

## donation


* [paypal.me/JensDiemer](https://www.paypal.me/JensDiemer)
* [Flattr This!](https://flattr.com/submit/auto?uid=jedie&url=https%3A%2F%2Fgithub.com%2Fjedie%2Fdjango-for-runners%2F)
* Send [Bitcoins](http://www.bitcoin.org/) to [1823RZ5Md1Q2X5aSXRC5LRPcYdveCiVX6F](https://blockexplorer.com/address/1823RZ5Md1Q2X5aSXRC5LRPcYdveCiVX6F)
