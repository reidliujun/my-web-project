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
    """An order, containing user, album, recipient, time, and cost information.

    album -- Needs to be deepcopied at the moment of order, as this
    way we can ensure that the user receives the same album as they have
    ordered. Otherwise, these is the danger that the album will be modified
    from time ordered to time printed. This is to be avoided.

    firstname, lastname, street_address, post_code_and_city, country -- Asked
    on a per order basis, as users are free to order their albums to whom ever
    they would like to. (default: last used values)

    item_cost -- (base cost) + (# of pages in the album) * (page cost)

    shipping_cost -- (country coefficient) * (order weight)

    total_cost -- item_count * item_cost + shipping_cost

    estimated_arrival_date -- Calculated based on country shipped to.

    """
    user = m.ForeignKey(User)
    album = m.ForeignKey(Album)  # TODO: This is bad, orders must be static.

    # Recipient/address information (NOTE: user does not have to be recipient!)
    firstname = m.CharField(max_length=255)
    lastname = m.CharField(max_length=255)
    street_address = m.CharField(max_length=255)
    post_code_and_city = m.CharField(max_length=255)
    country = m.CharField(max_length=255)

    # Item names, counts, costs, and relevant dates/times
    item_count = m.PositiveSmallIntegerField(default=1)  # TODO: multipl albums
    order_weight = m.FloatField(default=50)  # TODO: item_count * album pages
    currency = m.CharField(max_length=3, default="EUR")
    item_cost = m.FloatField(default=55)  # TODO: Change this to do the math.
    shipping_cost = m.FloatField(default=10)  # TODO: calculate this
    total_cost = m.FloatField(default=65)  # TODO: make this calculate
    # TODO: status choices
    status = m.CharField(max_length=255, default="Awaiting confirmation")
    time_placed = m.DateTimeField('Order time', default=datetime.datetime.now())
    # TODO: should do math
    estimated_arrival_date = m.DateTimeField('Estimated arrival date',
                                             default=datetime.datetime.now()+datetime.timedelta(days=10))

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

    def get_order_details(self):
        """Returns a list of user-relevant order details for template use. """
        details = [
            ["Album name:",
             self.album.title],
            ["Order status:",
             self.status],
            ["Time ordered:",
             self.time_placed],
            ["Estimated time of arrival:",
             self.estimated_arrival_date],
            ["Cost per copy:",
             "%s %.2f" % (self.currency, self.item_cost)],
            ["Copies ordered:",
             self.item_count],
            ["Total cost of shipping:",
             "%s %.2f" %
             (self.currency, self.shipping_cost)],
            ["Total paid:",
             "%s %.2f" % (self.currency, self.total_cost)],
        ]
        return details

    def __unicode__(self):  # TODO: What is this?
        return "Order:" + self.user.username + ";"

    ''' Generate the checksum value according to user pid, sid, amount and the token, 
        will be used for verification in the order system.'''
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
    title = m.CharField(max_length=30,blank=True,null=True)
    # FIXME: This is bad, we have to upload to user specific directories
    # imgfile = m.ImageField(upload_to='documents/%Y/%m/%d',blank=True,null=True)
    remote_path = m.URLField(blank=False, null=False)
    page = m.ManyToManyField(Page)
    user = m.ManyToManyField(User)
    album = m.ManyToManyField(Album)

    def __unicode__(self):
        return self.remote_path

    # def delete(self, *args, **kwargs):
    #     # get the page and storage before delete
    #     storage, path = self.imgfile.storage, self.imgfile.path
    #     # Delete the model before the file
    #     super(Image, self).delete(*args, **kwargs)
    #     # Delete the imagefile after the model
    #     storage.delete(path)
