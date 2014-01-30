# -*- coding: utf-8 -*-
from django.db import models as m
from django.contrib.auth.models import User
from django.db.models.signals import pre_delete
from django.dispatch.dispatcher import receiver


class Album(m.Model):
    title = m.CharField(max_length=255)
    public_url_suffix = m.CharField(max_length=255)
    collaboration_url_suffix = m.CharField(max_length=255)
    user = m.ManyToManyField(User)
    def __unicode__(self):
        return self.title


class Order(m.Model):
    user = m.ForeignKey(User)
    name = m.CharField(max_length=255)
    street_address = m.CharField(max_length=255)
    post_code_and_city = m.CharField(max_length=255)
    country = m.CharField(max_length=255)
    order_status = m.CharField(max_length=255)  # need to think about this
    order_time = m.DateTimeField(default=False)
    shipping_time = m.DateTimeField()
    # def __unicode__(self):
    #     return self.user


class Page(m.Model):
    album = m.ForeignKey(Album)
    layout = m.PositiveSmallIntegerField()
    number = m.PositiveSmallIntegerField()
    def __unicode__(self):
        return "Album:" + self.album.title + "; Page:" + str(self.number)

# class Photo(m.Model):
#     album = m.ManyToManyField(Album)
#     page = m.ManyToManyRel(Page)
class Image(m.Model):
    title = m.CharField(max_length=30)
    imgfile = m.ImageField(upload_to='documents/%Y/%m/%d')
    page = m.ManyToManyField(Page)
    user = m.ManyToManyField(User)
    album = m.ManyToManyField(Album)
    def __unicode__(self):
        return self.title

    def delete(self, *args, **kwargs):
        # get the page and storage before delete
        storage, path = self.imgfile.storage, self.imgfile.path
        # Delete the model before the file
        super(Image, self).delete(*args, **kwargs)
        # Delete the imagefile after the model
        storage.delete(path)
