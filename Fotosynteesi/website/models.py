#!/usr/bin/env python
# coding: utf-8
from django.contrib.auth.models import User
from django.db import models as m
from django.db import IntegrityError
from django.utils.text import slugify
import datetime
from uuid import uuid4

# Constants
SELLER_ID = 'group42'
CHECKSUM_TOKEN = '01d46c1d7f4cbe9686f7d1d8aec559d6'
BASE_CURRENCY = 'EUR'
BASE_UNIT_COST = 22.5  # in BASE_CURRENCY
COST_PER_PAGE = 1.35  # in BASE_CURRENCY


class Album(m.Model):
    """Docstring goes here. """

    # this allows for us to use user.albums to get a user's albums
    user = m.ForeignKey(User, related_name='albums')

    # this feature adds some complications to the project, may want to drop
    # collaborators = m.ManyToManyField(User)

    title_string = m.CharField(max_length=50)
    title_slug = m.SlugField()
    public_url_suffix = m.SlugField(max_length=32, blank=True)
    collaboration_url_suffix = m.SlugField(max_length=20, blank=True)

    def last_page_number(self):
        """Helper function for add_page().

        """
        # Query set containing all page objects / (this hits database)
        pp_all_qset = Page.objects.select_related('album')

        # Query set containing all page objects in this album
        pp_album_qset = pp_all_qset.filter(album=self)

        # Query set containing all page objects in this album rev sorted by #
        pp_album_qset_sorted = pp_album_qset.order_by('-number')

        # Now we can do many things: last page number, etc.

        # List containing all page objects in this album rev sorted by #
        pp_album_list_sorted = list(pp_album_qset_sorted)

        # First page object from the reverse sorted list
        last_page_object = pp_album_list_sorted[0]

        last_page_number = last_page_object.number

        if not last_page_number.__class__ == int:
            errmsg = "Get page number failed, got %s instead of int."
            raise TypeError(errmsg % last_page_number.__class__)

        return last_page_number

    def add_page(self, page_obj, location_index):
        """
        """

        if location_index is None:
            location_index = self.last_page_number() + 1

        page_obj.number = location_index

        if page_obj.number.__class__ != int:
            errmsg = "Add page failed, page number was reported as type %s."
            raise TypeError(errmsg % page_obj.number.__class__)
        if page_obj.number < 0:
            raise ValueError("Add page failed, tried add to negative index.")

    def generate_url_suffix(self, which):
        """Generates a random string, 32 characters in length, and saves it in
        the appropriate variable within the Album object. """
        if which == 'public':
            self.public_url_suffix = str(uuid4()).replace('-', '')
        elif which == 'collaboration':
            self.collaboration_url_suffix = str(uuid4()).replace('-', '')
        else:
            raise ValueError  # TODO: remove after testing (make actual tests)

    def calculate_item_cost(self):
        page_count = Page.objects.filter(album=self).count()
        return BASE_UNIT_COST + COST_PER_PAGE * page_count

    def save(self, *args, **kwargs):
        """Converts title_string to unicode and creates title_slug on save. """
        if self.title_string == '':
            raise IntegrityError("self.title_string cannot be blank.")
        self.title_string = unicode(self.title_string)
        self.title_slug = slugify(self.title_string)
        super(Album, self).save(*args, **kwargs)

    def __unicode__(self):
        """The string representation of this object is its title. """
        return self.title_string


class Page(m.Model):
    album = m.ForeignKey(Album, related_name='pages')
    layout = m.PositiveSmallIntegerField(default=1)
    number = m.PositiveSmallIntegerField(null=True)
    # front_cover = m.BooleanField(default=False) TODO: implement this?
    # back_cover = m.BooleanField(default=False) TODO: implement this?

    def get_last(self):
        album_pages = Page.objects.filter(album=self.album)
        last_page = album_pages.order_by('-number')[0]
        if last_page.number < 0:
            return 0
        return last_page.number

    def activate(self, to):
        active_album_pages = Page.objects.filter(album=self.album,
                                                 number__gte=to)
        for page in active_album_pages:
            page.number += 1
        self.number = to

    def deactivate(self):
        active_album_pages = Page.objects.filter(album=self.album,
                                                 number__gt=self.number)
        self.number = -1
        for page in active_album_pages:
            page.number -= 1

    def __unicode__(self):
        return str(self.number) + " in "  # + self.album.title


class Image(m.Model):
    """Represents a single referenced (or uploaded) photograph. """
    title = m.CharField(max_length=30)
    # FIXME: This is bad, we have to upload to user specific directories
    imgfile = m.ImageField(upload_to='documents/%Y/%m/%d')
    page = m.ManyToManyField(Page)
    user = m.ManyToManyField(User)
    album = m.ManyToManyField(Album)

    def __unicode__(self):
        return self.title

    def delete(self, *args, **kwargs):
        """Docstring goes here. """
        # get the page and storage before delete
        storage, path = self.imgfile.storage, self.imgfile.path
        # Delete the model before the file
        super(Image, self).delete(*args, **kwargs)
        # Delete the imagefile after the model
        storage.delete(path)


class Order(m.Model):
    """An order, containing user, album, recipient, time, and cost information.

    album -- Needs to be deepcopied at the moment of order, as this
    way we can ensure that the user receives the same album as they have
    ordered. Otherwise, these is the danger that the album will be modified
    from time ordered to time printed. This is to be avoided.

    firstname, lastname, street_address, post_code_and_city, country -- Asked
    on a per order basis, as users are free to order their albums to whom ever
    they would like to. (default: last used values)

    item_cost -- (BASE_UNIT_COST) + (# of pages in the album) * (COST_PER_PAGE)
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
    currency = m.CharField(max_length=3, default="EUR")
    item_cost = m.FloatField(default=BASE_UNIT_COST)  # TODO: Change this to do the math.
    shipping_cost = m.FloatField(default=10)  # TODO: calculate this
    total_cost = m.FloatField(default=65)  # TODO: make this calculate
    # TODO: status choices
    status = m.CharField(max_length=255, default="Awaiting confirmation")
    time_placed = m.DateTimeField(default=datetime.datetime.now())
    # TODO: should do math
    estimated_arrival_date = m.DateTimeField(default=datetime.datetime.now()+datetime.timedelta(days=10))

    # Payment ID to identify the payment used for this order
    pid = m.CharField(max_length=255)

    sid = m.CharField(max_length=255, default=SELLER_ID)

    success_url = m.CharField(max_length=255, blank=True, null=True)
    cancel_url = m.CharField(max_length=255, blank=True, null=True)
    error_url = m.CharField(max_length=255, blank=True, null=True)
    checksum = m.CharField(max_length=255)

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

    def generate_checksum(self):
        """Generate the checksum value according to user pid, sid, amount and
        the token, will be used for verification in the order system.

        """
        import hashlib
        amount = unicode(self.total_cost)
        checksumstr = ("pid=" + self.pid +
                       "&sid=" + self.sid +
                       "&amount=" + amount +
                       "&token=" + CHECKSUM_TOKEN)

        mm = hashlib.md5.new(checksumstr)
        self.checksum = mm.hexdigest()
        return self.checksum
        # import md5
        # checksumstr = "pid="+self.pid+"&sid="+self.sid+"&amount="+self.total_cost+"&token=01d46c1d7f4cbe9686f7d1d8aec559d6"
        # mm = md5.new(checksumstr)  # FIXME: the module md5 is deprecated
        # self.checksum = mm.hexdigest()
        # return self.checksum

    def __unicode__(self):
        return "%s copies of %s ordered on %s" % (
            self.item_count, self.album.title, self.time_placed)

