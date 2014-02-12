#!/usr/bin/env python
# coding: utf-8

from django.test import TestCase
from models import *

import unittest


class ModelTestCase(TestCase):

    def setUp(self):
        self.u1 = User.objects.create(username='Alice')
        self.u2 = User.objects.create(username='Bob')

    def test_creating_an_album_with_minimum_parameters(self):
        a1 = Album.objects.create(user=self.u1)

        print a1.title
        self.assertEqual(a1.user, self.u1)
        self.assertEqual(a1.title, '')
        self.assertEqual(a1.public_url_suffix, '')
        self.assertEqual(a1.collaboration_url_suffix, '')

    def test_creating_an_album_with_legit_parameters(self):
        a1 = Album.objects.create(user=self.u1, title="Alice's Album")

        self.assertEqual(a1.user, self.u1)
        self.assertEqual(a1.title, "Alice's Album")
        self.assertEqual(a1.public_url_suffix, '')
        self.assertEqual(a1.collaboration_url_suffix, '')

    def tearDown(self):
        self.u1.delete()
        self.u2.delete()

if __name__ == '__main__':
    unittest.main()
