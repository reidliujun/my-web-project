# -*- coding: utf-8 -*-
from django.db import models as m
from django.contrib.auth.models import User
from django.db.models.signals import pre_delete
from django.dispatch.dispatcher import receiver
import datetime


class Album(m.Model):
    title = m.CharField(max_length=255)
    public_url_suffix = m.CharField(max_length=255)
    collaboration_url_suffix = m.CharField(max_length=255)
    user = m.ManyToManyField(User)

    def __unicode__(self):
        return self.title


class Order(m.Model):
    user = m.ForeignKey(User)
    album = m.ForeignKey(Album)
    firstname = m.CharField(max_length=255)
    lastname = m.CharField(max_length=255)
    street_address = m.CharField(max_length=255)
    post_code_and_city = m.CharField(max_length=255)
    country = m.CharField(max_length=255)

    # Item counts, costs, and relevant dates/times
    item_count = m.CharField(max_length=255)
    total_cost = m.CharField(max_length=255)
    time_placed = m.DateTimeField('Order time', default=datetime.datetime.now())
    estimated_arrival_date = m.DateTimeField('Estimated arrival date', default=datetime.datetime.now()+datetime.timedelta(days=10))

    # Payment id to identify this payment
    pid = m.CharField(max_length=255)

    # sid = group42
    sid = m.CharField(max_length=255)

    success_url = m.CharField(max_length=255, blank=True, null=True)
    cancel_url = m.CharField(max_length=255, blank=True, null=True)
    error_url = m.CharField(max_length=255, blank=True, null=True)
    checksum = m.CharField(max_length=255)
    # order_status = m.CharField(max_length=255) # need to think about this
    # time_placed = m.DateTimeField()
    # def __unicode__(self):
    #     return self.user
    def __unicode__(self):
        return "Order:" + self.user.username + ";" 

    def checksumfunc(self):
        """Calculates the sumsecurity for payment system. """
        import md5
        checksumstr = "pid="+self.pid+"&sid="+self.sid+"&amount="+self.total_cost+"&token=01d46c1d7f4cbe9686f7d1d8aec559d6"
        mm = md5.new(checksumstr)  # FIXME: the module md5 is deprecated
        self.checksum = mm.hexdigest()
        return self.checksum


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
