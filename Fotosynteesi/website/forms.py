from django import forms

class ImgForm(forms.Form):
    imgfile = forms.ImageField(label='')

