import logging

# https://github.com/jedie/django-for-runners
from for_runners.services.gpx_calculate_values import calculate_values
from for_runners.services.gpx_save_gpx import save_gpx_file
from for_runners.services.gpx_svg_generator import generate_svg


log = logging.getLogger(__name__)


def gpx_pre_save_handler(sender, instance, update_fields, **kwargs):
    if instance.gpx:
        calculate_values(gpx_track=instance)


def gpx_post_save_handler(sender, instance, created, update_fields, **kwargs):
    if not instance.track_svg:

        generate_svg(gpx_track=instance, force=False)

        save_gpx_file(gpx_track=instance, force=False)

        log.warning("Save gpx file, too!")
