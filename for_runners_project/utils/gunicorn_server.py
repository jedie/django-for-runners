"""
Based on http://docs.gunicorn.org/en/stable/custom.html
"""

import multiprocessing

import gunicorn.app.base
from django.core.wsgi import get_wsgi_application


class GunicornApplication(gunicorn.app.base.BaseApplication):
    def __init__(self, application, **options):
        self.options = options
        self.application = application
        super().__init__()

    def load_config(self):
        for key, value in self.options.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application


def get_gunicorn_application(address="127.0.0.1:8000"):
    print(f"Start gunicorn on: {address!r}")
    wsgi_application = get_wsgi_application()
    number_of_workers = (multiprocessing.cpu_count() * 2) + 1
    return GunicornApplication(wsgi_application, bind=address, workers=number_of_workers)
