from django.conf import settings
from django.conf.urls import include, static, url
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.urls import path
from django.views.generic import RedirectView

from for_runners.views.media_files import UserMediaView


admin.autodiscover()


urlpatterns = i18n_patterns(
    path("admin/", admin.site.urls),

    # until there is not real CMS pages: redirect to the interesting admin page:
    url(r"^$", RedirectView.as_view(url="/admin/for_runners/gpxmodel/")),
)


urlpatterns = [
    # TODO: Change from user name to ID?
    path('media/<slug:user_name>/<path:path>', UserMediaView.as_view()),
] + urlpatterns


if settings.SERVE_FILES:
    urlpatterns += static.static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [url(r'^__debug__/', include(debug_toolbar.urls))] + urlpatterns
