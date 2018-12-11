from django.db import models
from django.utils.translation import ugettext_lazy as _


def gpx_upload_to(instance, filename):
    return instance.get_gpx_filepath()
    date_prefix = instance.start_time.strftime("%Y_%m")
    svg_upload_path = "track_svg_%s/%s.svg" % (date_prefix, self.get_prefix_id())
    log.debug("Ignore source filename: %r upload to: %r", filename, svg_upload_path)
    return svg_upload_path


class GpxFileField(models.FileField):

    def __init__(self, **kwargs):
        kwargs["upload_to"] = gpx_upload_to
        super().__init__(**kwargs)
