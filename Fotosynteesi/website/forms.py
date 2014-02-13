#!/usr/bin/env python
# coding: utf-8
from django import forms


class ImgForm(forms.Form):
    imgfile = forms.ImageField(label='')

