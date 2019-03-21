"""
Based on http://docs.gunicorn.org/en/stable/custom.html
"""

import multiprocessing

import gunicorn.app.base
from gunicorn.six import iteritems

from django.core.wsgi import get_wsgi_application


class GunicornApplication(gunicorn.app.base.BaseApplication):
    def __init__(self, application, options=None):
        self.options = options or {}
        self.application = application
        super().__init__()

    def load_config(self):
        config = dict(
            [(key, value) for key, value in iteritems(self.options) if key in self.cfg.settings and value is not None]
        )
        for key, value in iteritems(config):
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application


def number_of_workers():
    return (multiprocessing.cpu_count() * 2) + 1


def get_gunicorn_application():
    wsgi_application = get_wsgi_application()
    options = {"bind": "%s:%s" % ("127.0.0.1", "8000"), "workers": number_of_workers()}
    return GunicornApplication(wsgi_application, options)
