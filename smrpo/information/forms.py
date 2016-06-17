from django import forms

class UploadFileForm(forms.Form):
    file = forms.FileField(
        label='Izberi datoteko',
        help_text='Maximalna velikost je 42 MB.'
    )