# Django-ForRunners

![Logo](https://github.com/jedie/django-for-runners/raw/main/for_runners/static/Django-ForRunners128.png "Logo") Store your GPX tracks of your running (or other sports activity) in django.

[![pytest](https://github.com/jedie/django-for-runners/workflows/test/badge.svg?branch=main)](https://github.com/jedie/django-for-runners/actions)
[![Coverage Status on codecov.io](https://codecov.io/gh/jedie/django-for-runners/branch/main/graph/badge.svg)](https://codecov.io/gh/jedie/django-for-runners)
[![django_yunohost_integration @ PyPi](https://img.shields.io/pypi/v/django_yunohost_integration?label=django_yunohost_integration%20%40%20PyPi)](https://pypi.org/project/django_yunohost_integration/)
[![Python Versions](https://img.shields.io/pypi/pyversions/django_yunohost_integration)](https://github.com/jedie/django-for-runners/blob/main/pyproject.toml)
[![License GPL](https://img.shields.io/pypi/l/django_yunohost_integration)](https://github.com/jedie/django-for-runners/blob/main/LICENSE)

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

## Django compatibility

| django-for-runners | django version | python              |
|--------------------|----------------|---------------------|
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


* [**dev**](https://github.com/jedie/django-for-runners/compare/v0.17.3...main)
  * TBC
* [03.04.2023 - v0.17.3](https://github.com/jedie/django-for-runners/compare/v0.17.2...v0.17.3):
  * Bugfix system check on fresh start with Postgres before migration is running
* [02.04.2023 - v0.17.2](https://github.com/jedie/django-for-runners/compare/v0.17.0...v0.17.2):
  * Bugfix packaging and missing files
* [02.04.2023 - v0.17.0](https://github.com/jedie/django-for-runners/compare/v0.16.0...v0.17.0):
  * Bugfix edit a `GpxModel` instance in admin with a large GPX track by remove the raw gpx XML as text field from admin change page
  * Add a admin action to download selected GPX tracks as ZIP archive
* [13.03.2023 - v0.16.0](https://github.com/jedie/django-for-runners/compare/v0.15.0...v0.16.0):
  * NEW: Attach files and images to "Event Participations"
  * Switch from Poetry to pip-tools
  * Add a new way to bootstrap the developer environment
* [29.09.2022 - v0.15.0](https://github.com/jedie/django-for-runners/compare/v0.14.0...v0.15.0):
  * Update requirements
  * Activate auto login for local dev. server, for easier developing.
  * Test against different Django Versions: 3.2, 4.0 and 4.1
  * Replace creole README with Markdown
* [16.08.2022 - v0.14.0](https://github.com/jedie/django-for-runners/compare/v0.13.0...v0.14.0):
  * Update to Django v3.2
  * Bugfix backup manage command
* [15.04.2022 - v0.13.0](https://github.com/jedie/django-for-runners/compare/v0.12.1...v0.13.0):
  * Switch git branch from "master" to "main"
  * Remove "/development/" and mode "/src/"
  * update requirements
* [22.11.2021 - v0.12.1](https://github.com/jedie/django-for-runners/compare/v0.12.0...v0.12.1):
  * update requirements
* [17.01.2021 - v0.12.0](https://github.com/jedie/django-for-runners/compare/v0.11.0...v0.12.0):
  * refactor project structure and add a deployment via docker-compose setup
  * installation as YunoHost app: [https://github.com/YunoHost-Apps/django-for-runners_ynh](https://github.com/YunoHost-Apps/django-for-runners_ynh)
  * Add django-axes and django-processinfo
  * Mock requests in tests
* [04.07.2020 - v0.11.0](https://github.com/jedie/django-for-runners/compare/v0.10.1...v0.11.0):
  * refactor gpx import code
  * update tests
  * Use poetry and add Makefile
  * update code style
* [09.08.2019 - v0.10.1](https://github.com/jedie/django-for-runners/compare/v0.10.0...v0.10.1):
  * Enhance "Event Participation" admin view: Add start date and costs in table
* [26.06.2019 - v0.10.0](https://github.com/jedie/django-for-runners/compare/v0.9.0...v0.10.0):
  * NEW: GPX Admin action to print a small overview from one or a few tracks
  * Accept optional server bind address, e.g.: `for_runners run-server 127.0.0.1:8080`
* [02.04.2019 - v0.9.0](https://github.com/jedie/django-for-runners/compare/v0.8.1...v0.9.0):
  * NEW: Update complete environment installation with: `for_runners update`
  * Move the SQlite database to virtualenv root dir, e.g.: `~/Django-ForRunners/Django-ForRunners-database.sqlite3`
  * NEW: save every gpx track to disk
  * NEW: Backup/export via cli: `$ for_runners backup`
  * NEW: export GPX Data via `django-import-export`
  * Create xdg-open desktop starter under linux here: `~/Django-ForRunners/Django-ForRunners`
  * refactor the startup process:
    * auto loop the server process
    * open web browser on first start
    * enable autotask
  * rename `for_runners_test_project` to `for_runners_project`
* [03.09.2018 - v0.8.1](https://github.com/jedie/django-for-runners/compare/v0.8.0...v0.8.1):
  * Fix "try-out" section in README, again ;(
* [03.09.2018 - v0.8.0](https://github.com/jedie/django-for-runners/compare/v0.7.1...v0.8.0):
  * NEW: shell script for easier boot/install, see above
* [02.09.2018 - v0.7.1](https://github.com/jedie/django-for-runners/compare/v0.7.0...v0.7.1):
  * Update to Django 2.1
  * Bugfix Tests
* [02.09.2018 - v0.7.0](https://github.com/jedie/django-for-runners/compare/v0.6.0...v0.7.0):
  * Use dygraphs in GPX Track change admin view
  * Sync mouse over from Elevation/Headrate/Cadence dygraphs to leaflet open streep map
  * Fix "try-out" section in README ([Thanks adsworth for reporting](https://github.com/jedie/django-for-runners/pull/1))
  * Add links from gpx tracks to other admin change view
  * Bugfixes
  * internals:
    * refactor stuff around track duration/length
    * move manipluation of list_display and list_filter [contributed by adsworth](https://github.com/jedie/django-for-runners/pull/2)
* [19.07.2018 - v0.6.0](https://github.com/jedie/django-for-runners/compare/v0.5.0...v0.6.0):
  * NEW: event participation
  * NEW: costs of event participation (e.g.: entry fee for the competition, cost of a T-Shirt etc.)
  * NEW: Display statistics of events/costs per user and total
* [04.07.2018 - v0.5.0](https://github.com/jedie/django-for-runners/compare/v0.4.0...v0.5.0):
  * remove Django-CMS
  * update to Django v2.0
  * NOTE: The migrations are simply replaced! So you must delete your database, e.g.: `src/django-for-runners$ rm test_project_db.sqlite3`
  * Add 'net duration' field, for the officially measured time and use it for calculations if available.
  * Create django manage command to fill some base data: `$ ./manage.py fill_basedata`
  * speedup by deactivating some django debug toolbar panels
* [26.06.2018 - v0.4.0](https://github.com/jedie/django-for-runners/compare/v0.3.0...v0.4.0):
  * combine track filters with statistic views
  * NEW: GPX info (See length, point count and Average distance in meters between the points)
  * NEW: Display GPX metadata
  * Add 'creator' to every track and use it as changelist filter
  * remove Streetmap image generated via [geotiler](https://pypi.org/project/geotiler/)
  * Speedup by using a cache for gpxpy instances
* [23.06.2018 - v0.3.0](https://github.com/jedie/django-for-runners/compare/v0.2.0...v0.3.0):
  * Start adding statistics (See screenshot above)
  * add weather information from [metaweather.com](https://www.metaweather.com/) to every track
* [21.06.2018 - v0.2.0](https://github.com/jedie/django-for-runners/compare/v0.1.1...v0.2.0):
  * Display elevations, heart_rates and cadence_values if available
  * Add kilometer markers to OpenStreetMap
* [15.06.2018 - v0.1.1](https://github.com/jedie/django-for-runners/compare/v0.1.0...v0.1.1):
  * a few bugfixes
* [15.06.2018 - v0.1.0](https://github.com/jedie/django-for-runners/compare/v0.0.4...v0.1.0):
  * Render interactive OpenStreetMap track map with Leaflet JS
* [12.06.2018 - v0.0.4](https://github.com/jedie/django-for-runners/compare/v0.0.3...v0.0.4):
  * Better Events model
  * GPX error handling
  * more tests
  * Bugfix for Python 3.5 (Geotiler needs Python 3.6 or later)
* [12.06.2018 - v0.0.3](https://github.com/jedie/django-for-runners/compare/v0.0.2...v0.0.3):
  * display min/average/max heart rate
  * use autotask to generate the MAP in background
* [31.05.2018 - v0.0.2](https://github.com/jedie/django-for-runners/compare/v0.0.1...v0.0.2):
  * generate SVG 'icon' from GPX track
* v0.0.1 - 30.05.2018
  * Just create a pre-alpha release to save the PyPi package name ;)

## links

| Homepage | [http://github.com/jedie/django-for-runners](http://github.com/jedie/django-for-runners)     |
| PyPi     | [https://pypi.org/project/django-for-runners/](https://pypi.org/project/django-for-runners/) |

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
