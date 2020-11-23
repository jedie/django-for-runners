"""
    Configuration for Gunicorn
"""
import multiprocessing


bind = 'django:8000'

# https://docs.gunicorn.org/en/latest/settings.html#workers
workers = multiprocessing.cpu_count() * 2 + 1

# https://docs.gunicorn.org/en/latest/settings.html#logging
loglevel = 'info'
accesslog = '-'  # log to stdout
errorlog = '-'  # log to stdout

# https://docs.gunicorn.org/en/latest/settings.html#pidfile
pidfile = '/tmp/gunicorn.pid'
