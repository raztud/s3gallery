from django import forms


class UploadFileForm(forms.Form):
    file = forms.FileField()
    comment = forms.CharField(widget=forms.Textarea)

