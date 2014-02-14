from django import forms
# from photologue.models import *

class UploadFileForm(forms.Form):
    # title = forms.CharField(max_length=50)
    # title_slug = forms.CharField(max_length=50)
    file  = forms.ImageField()


# class CreateGallery(forms.Form):
# 	title = forms.CharField(max_length=50)