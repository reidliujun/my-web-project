from django.contrib import admin
from django import forms
from django.conf import settings

from .models import *



class GalleryAdminForm(forms.ModelForm):

    class Meta:
        model = Gallery


class GalleryAdmin(admin.ModelAdmin):
    list_display = ('title', 'date_added', 'photo_count', 'is_public')
    list_filter = ['date_added', 'is_public']
    date_hierarchy = 'date_added'
    prepopulated_fields = {'title_slug': ('title',)}
    filter_horizontal = ('photos',)
    form = GalleryAdminForm


class PhotoAdminForm(forms.ModelForm):

    class Meta:
        model = Photo


class PhotoAdmin(admin.ModelAdmin):
    list_display = ('title', 'date_taken', 'date_added', 'is_public', 'view_count', 'admin_thumbnail')
    list_filter = ['date_added', 'is_public']
    search_fields = ['title', 'title_slug', 'caption']
    list_per_page = 10
    prepopulated_fields = {'title_slug': ('title',)}
    form = PhotoAdminForm



class GalleryUploadAdmin(admin.ModelAdmin):

    def has_change_permission(self, request, obj=None):
        return False  # To remove the 'Save and continue editing' button


admin.site.register(Gallery, GalleryAdmin)
admin.site.register(GalleryUpload, GalleryUploadAdmin)
admin.site.register(Photo, PhotoAdmin)
