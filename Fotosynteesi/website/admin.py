from django.contrib import admin
from django import forms
from .models import *


class ImageAdminForm(forms.ModelForm):

    class Meta(object):
        model = Image


class ImageAdmin(admin.ModelAdmin):
    list_display = ['remote_path']
    form = ImageAdminForm


class AlbumAdmin(admin.ModelAdmin):
    list_display = ['title_string']


class PageAdmin(admin.ModelAdmin):
    pass


class OrderAdmin(admin.ModelAdmin):
    list_display = ['user', 'time_placed']

admin.site.register(Image, ImageAdmin)
admin.site.register(Album, AlbumAdmin)
admin.site.register(Page, PageAdmin)
admin.site.register(Order, OrderAdmin)
