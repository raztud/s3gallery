# coding: utf-8

from django import forms
from captcha.fields import ReCaptchaField


class UploadFileForm(forms.Form):
    uploadedfile = forms.FileField()
    comment = forms.CharField(widget=forms.Textarea)
    captcha = ReCaptchaField(attrs={
      'theme': 'clean',
    })

