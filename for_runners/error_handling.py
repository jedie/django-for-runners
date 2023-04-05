import logging
import traceback

from django.conf import settings


log = logging.getLogger(__name__)


def capture_exception(err) -> None:
    if settings.RAISE_CAPTURE_EXCEPTIONS:
        raise

    if settings.DEBUG or settings.PRINT_TRACEBACKS:
        traceback.print_exception(err)  # Normal, shot Traceback
