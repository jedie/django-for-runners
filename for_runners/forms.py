from django import forms

class UploadGpxFileForm(forms.Form):
    gpx_files = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))

    def send_email(self):
        # send email using the self.cleaned_data dictionary
        pass
