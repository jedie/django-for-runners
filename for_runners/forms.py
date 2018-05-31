"""
    created 30.05.2018 by Jens Diemer <opensource@jensdiemer.de>
    :copyleft: 2018 by the django-for-runners team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""
from django import forms

class UploadGpxFileForm(forms.Form):
    gpx_files = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))

    def send_email(self):
        # send email using the self.cleaned_data dictionary
        pass
