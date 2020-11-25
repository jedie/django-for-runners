import logging

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.views.generic.base import View
from django.views.static import serve


logger = logging.getLogger(__name__)


class UserMediaView(View):
    """
    Serve MEDIA_URL files, but check the current user:
    """

    def get(self, request, user_name, path):
        # TODO: Change from user name to ID?
        media_path = f'{user_name}/{path}'

        logger.debug('Serve: %r', media_path)

        if not request.user.is_superuser:
            if request.user.username != user_name:
                # A user tries to access a file from a other use?
                if request.user.id is None:
                    logger.error(f'Anonymous try to access files from: {user_name!r}')
                else:
                    logger.error(f'Wrong user ID: {request.user.id!r} is not {user_name!r}')
                raise PermissionDenied

        # Send the file to the user:
        return serve(
            request,
            path=media_path,
            document_root=settings.MEDIA_ROOT,
            show_indexes=False
        )
