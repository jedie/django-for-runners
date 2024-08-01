import datetime
import logging

from django.conf import settings
from requests import Response, Session
from requests_cache import CachedSession
from retry_requests import retry

from for_runners import __version__


log = logging.getLogger(__name__)

USER_AGENT = f'django-for-runners {__version__}'


if settings.REQUEST_CACHE:
    log.info('Request CachedSession() used.')
    _session = CachedSession(
        cache_name='for_runners_requests_cache',
        use_cache_dir=True,  # Save files in the default user cache dir
        expire_after=datetime.timedelta(days=1),
    )
else:
    # e.g.: don't use cache in tests!
    log.warning('No request CachedSession() used!')
    _session = Session()

retry_session = retry(_session, retries=5, backoff_factor=0.2)


def request_get(url: str, *, timeout: int = 5, params: dict | None = None) -> Response:
    response = retry_session.get(
        url,
        params=params,
        headers={'user-agent': USER_AGENT},
        timeout=timeout,
    )
    return response
