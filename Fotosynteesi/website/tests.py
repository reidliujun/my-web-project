#!/usr/bin/env python
# coding: utf-8

from django.test import TestCase, TransactionTestCase
from django.db.models import Q
from django.db import IntegrityError
from django.db.transaction import TransactionManagementError
from models import *

import unittest


class ModelTestCase(TransactionTestCase):

    def setUp(self):
        u1 = User.objects.create(username='alice12')
        u2 = User.objects.create(username='bobmeister')
        u3 = User.objects.create(username='carolynn')

        a1 = Album.objects.create(user=u1, title_string="Alice's Album")
        a2 = Album.objects.create(user=u2, title_string="Spring Break 2013")

        self.p1 = Page.objects.create(album=a1)
        p11 = Page.objects.create(album=a1)
        p2 = Page.objects.create(album=a2)

    def test_album_creation(self):
        u1 = User.objects.get(username='alice12')
        a1 = Album.objects.get(user=u1)

        self.assertEqual(a1.user, u1)
        self.assertEqual(a1.title_string, "Alice's Album")
        self.assertEqual(a1.title_slug, "alices-album")
        self.assertEqual(a1.public_url_suffix, '')
        self.assertEqual(a1.collaboration_url_suffix, '')

        u3 = User.objects.get(username='carolynn')
        Album.objects.create(user=u3, title_string="Spring Break 2013")

        albums = list(Album.objects.filter(title_string="Spring Break 2013"))
        self.assertEqual(len(albums), 2)

    def test_page_creation(self):
        self.assertRaises(IntegrityError, Page.objects.create)

        u1 = User.objects.get(username='alice12')
        a1 = Album.objects.get(user=u1)

        self.assertEqual(a1, self.p1.album)

    def tearDown(self):
        User.objects.filter(~Q(username='admin')).delete()
        Album.objects.all().delete()
        Page.objects.all().delete()
        Image.objects.all().delete()
        Order.objects.all().delete()

if __name__ == '__main__':
    unittest.main()