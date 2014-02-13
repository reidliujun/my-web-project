#!/usr/bin/env python
# coding: utf-8

from django.test import TestCase, TransactionTestCase
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.db.transaction import TransactionManagementError
from models import *

import unittest


class ModelTestCase(TransactionTestCase):

    def setUp(self):
        u1 = User.objects.create(username='alice12')
        u2 = User.objects.create(username='bobmeister')
        u3 = User.objects.create(username='carolynn')
        u4 = User.objects.create(username='dave_callahan')

        a1 = Album.objects.create(user=u1, title_string="Alice's Album")
        a2 = Album.objects.create(user=u2, title_string="Spring Break 2013")

        self.p1 = Page.objects.create(album=a1)
        p11 = Page.objects.create(album=a1)
        p2 = Page.objects.create(album=a2)
        p22 = Page.objects.create(album=a2)
        p222 = Page.objects.create(album=a2)

    def test_album_creation(self):
        u1 = User.objects.get(username='alice12')
        a1 = Album.objects.get(user=u1)

        # Checks that album is created as per specs
        self.assertEqual(a1.user, u1)
        self.assertEqual(a1.title_string, "Alice's Album")
        self.assertEqual(a1.title_slug, "alices-album")
        self.assertEqual(a1.public_url_suffix, '')
        self.assertEqual(a1.collaboration_url_suffix, '')

        # Create album without giving a title
        u4 = User.objects.get(username='dave_callahan')
        Album.objects.create(user=u4)
        self.assertRaises(ObjectDoesNotExist, Album.objects.get, user=u4)

        # Same title_string, but different user
        u3 = User.objects.get(username='carolynn')
        Album.objects.create(user=u3, title_string="Spring Break 2013")
        albums = list(Album.objects.filter(title_string="Spring Break 2013"))
        self.assertEqual(len(albums), 2)

        # Create album with a title_string not unique to that user
        Album.objects.create(user=u1, title_string="Alice's Album")
        albums = list(Album.objects.filter(user=u1))
        self.assertEqual(len(albums), 1)

        # Create album with a title_string that results in a title_slug not
        # unique to that user
        Album.objects.create(user=u1, title_string="Ali'ces Album")
        albums = list(Album.objects.filter(user=u1))
        self.assertEqual(len(albums), 1)

    def test_page_creation(self):

        u1 = User.objects.get(username='alice12')
        a1 = Album.objects.get(user=u1)

        # Checks that page was associated with correct album
        self.assertEqual(self.p1.album, a1)

        # Checks that page has correct default layout
        self.assertEqual(self.p1.layout, 1)

        # Checks that pages cannnot be created without required params
        self.assertRaises(IntegrityError, Page.objects.create)

        # Checks that pages cannot be created without album association
        self.assertRaises(IntegrityError, Page.objects.create, number=1)

        # Checks that pages cannot be created without a page number
        u2 = User.objects.get(username='bobmeister')
        a2 = Album.objects.get(user=u2)
        self.assertRaises(IntegrityError, Page.objects.create, album=a2)

    def tearDown(self):
        User.objects.filter(~Q(username='admin')).delete()
        Album.objects.all().delete()
        Page.objects.all().delete()
        Image.objects.all().delete()
        Order.objects.all().delete()

if __name__ == '__main__':
    unittest.main()