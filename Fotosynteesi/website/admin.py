from django.contrib import admin
from django import forms
from .models import *
# Register your models here.

class ImageAdminForm(forms.ModelForm):

    class Meta:
        model = Image

class ImageAdmin(admin.ModelAdmin):
    list_display = ['title']
    form = ImageAdminForm


class AlbumAdmin(admin.ModelAdmin):
    list_display = ['title']


class PageAdmin(admin.ModelAdmin):
    pass


class OrderAdmin(admin.ModelAdmin):
    list_display = ['user', 'time_placed']

admin.site.register(Image, ImageAdmin)
admin.site.register(Album, AlbumAdmin)
admin.site.register(Page, PageAdmin)
admin.site.register(Order, OrderAdmin)
