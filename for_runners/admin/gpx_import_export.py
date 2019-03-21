"""
    https://django-import-export.readthedocs.io/en/latest/getting_started.html
"""

from import_export import resources
from import_export.fields import Field

# https://github.com/jedie/django-for-runners
from for_runners.models import GpxModel


class GpxModelResource(resources.ModelResource):
    """
    TODO: Use it in for_runners.management.commands.backup.Command
    """

    start_time = Field()
    name = Field()
    event = Field()
    duration = Field()
    pace = Field()
    heart_rate = Field()
    temperature = Field()
    weather = Field()
    username = Field()

    def dehydrate_start_time(self, track):
        return track.start_time

    def dehydrate_name(self, track):
        return track.short_name(start_time=False)

    def dehydrate_event(self, track):
        # Note: track.participation.event.verbose_name() is used in short_name() ;)
        return "x" if track.participation else ""

    def dehydrate_length(self, track):
        return round(track.length / 1000, 2)

    def dehydrate_duration(self, track):
        return track.human_duration()

    def dehydrate_pace(self, track):
        return track.human_pace()

    def dehydrate_heart_rate(self, track):
        if track.heart_rate_avg:
            return "%i b/m" % track.heart_rate_avg

    def dehydrate_temperature(self, track):
        if track.start_temperature:
            return "%i°C" % round(track.start_temperature, 1)

    def dehydrate_weather(self, track):
        if track.start_temperature:
            return track.start_weather_state

    def dehydrate_username(self, track):
        return track.tracked_by.username

    class Meta:
        model = GpxModel
        fields = (
            "start_time",
            "name",
            "event",
            "length",
            "duration",
            "pace",
            "heart_rate",
            "temperature",
            "weather",
            "creator",
            "username",
        )
