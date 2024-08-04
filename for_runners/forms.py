"""
    created 30.05.2018 by Jens Diemer <opensource@jensdiemer.de>
    :copyleft: 2018 by the django-for-runners team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from django import forms


class MultipleFileInput(forms.ClearableFileInput):
    # https://docs.djangoproject.com/en/4.2/topics/http/file-uploads/#uploading-multiple-files
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result


class UploadFilesForm(forms.Form):
    files = MultipleFileField()

    def send_email(self):
        # send email using the self.cleaned_data dictionary
        pass


INITIAL_DISTANCE = 2


class DistanceStatisticsForm(forms.Form):
    distance = forms.FloatField(
        label="Distance (km)",
        max_value=10,
        min_value=0.1,
        initial=INITIAL_DISTANCE,
        help_text="Gradation in kilometers to summarize the data.",
    )
