# -*- coding: utf-8 -*-
"""
tests.py

"""

import os
import sys
import logging
import unittest

from ssp_director import *

from pprint import pprint

#: These tests will only work on an actual SSP account/install!

API_KEY = 'hosted-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx' # removed
API_PATH = 'xxxxxxxx.slideshowpro.com' # removed

TEST_ALBUM_ID = 441917
TEST_GALLERY_ID = 81173
TEST_CONTENT_ID = 9239443

# --------------------------------------------------------------------
# Director Test
# --------------------------------------------------------------------

class DirectorTest(unittest.TestCase):

    def setUp(self):
        self.director = Director(api_key=API_KEY, api_path=API_PATH)

    #
    # Director Methods
    # ----------------------------------------------------------------

    def test_director_connection(self):
        self.assertRaises(ValueError, Director, api_key='#bad', api_path='#bad')

        self.director.api_path = '#bad'

        respone = self.director._get('app_version')
        self.assertIsInstance(respone, dict)

    #
    # Application Methods
    # ----------------------------------------------------------------

    def test_application_get_version(self):
        version = self.director.get_version()
        self.assertIsInstance(version, basestring)

    def test_application_get_limits(self):
        limits = self.director.get_limits()
        self.assertIsInstance(limits, dict)

    def test_application_get_totals(self):
        totals = self.director.get_totals()
        self.assertIsInstance(totals, dict)

    #
    # Gallery Methods
    # ----------------------------------------------------------------

    def test_gallery_get_galleries(self):
        galleries = self.director.get_galleries()
        self.assertIsInstance(galleries, list)

    def test_gallery_get_gallery(self):
        self.assertRaises(DirectorError, self.director.get_gallery, gallery_id=10001)

        gallery = self.director.get_gallery(TEST_GALLERY_ID)
        self.assertIsInstance(gallery, dict)

        gallery = self.director.get_gallery(TEST_GALLERY_ID, with_content=False)
        self.assertIsInstance(gallery, dict)

    #
    # Album Methods
    # ----------------------------------------------------------------

    def test_album_get_albums(self):
        albums = self.director.get_albums()
        self.assertIsInstance(albums, list)

        albums = self.director.get_albums(only_published=True)
        self.assertIsInstance(albums, list)

        albums = self.director.get_albums(only_active=False, exclude_smart=True, only_published=True, list_only=False)
        self.assertIsInstance(albums, list)

        albums = self.director.get_albums(tags=['vacation', 'summer', ''], tags_exclusive=True)
        self.assertIsInstance(albums, list)

    def test_album_get_album(self):
        album = self.director.get_album(TEST_ALBUM_ID)
        self.assertIsInstance(album, dict)

        album = self.director.get_album(TEST_ALBUM_ID, only_active=False)
        self.assertIsInstance(album, dict)

    def test_album_get_galleries_by_album(self):
        galleries = self.director.get_galleries_by_album(TEST_ALBUM_ID)
        self.assertIsInstance(galleries, list)

        galleries = self.director.get_galleries_by_album(TEST_ALBUM_ID, exclude=(81173, 81146))
        self.assertIsInstance(galleries, list)

    #
    # Content Methods
    # ----------------------------------------------------------------

    def test_content_get_contents(self):
        contents = self.director.get_contents()
        self.assertIsInstance(contents, list)

        # contents = self.director.get_contents(limit=10)
        # contents = self.director.get_contents(only_images=True)
        # contents = self.director.get_contents(only_active=False)
        # contents = self.director.get_contents(tags=['suv', 'porsche'], tags_exclusive=True)
        # contents = self.director.get_contents(limit=5, sort_on='random')
        # contents = self.director.get_contents(limit=5, sort_direction='asc')
        # contents = self.director.get_contents(scope='album', scope_id=441975)

        images = self.director.get_images()
        self.assertIsInstance(images, list)

    def test_content_get_content(self):
        content = self.director.get_content(TEST_CONTENT_ID)
        self.assertIsInstance(content, dict)

    #
    # User Methods
    # ----------------------------------------------------------------

    def test_user_get_users(self):
        users = self.director.get_users()
        self.assertIsInstance(users, list)

        users = self.director.get_users(scope='album', scope_id=TEST_ALBUM_ID)
        self.assertIsInstance(users, list)

    #
    # Format Methods
    # ----------------------------------------------------------------

    def test_format_methods(self):
        self.director.clear_formats()
        self.director.add_format('thumb', 150, 120)
        self.director.add_user_format('medium', 150, 120)
        self.director.set_preview_format(132322, 123223)

        self.assertEqual(len(self.director._formats['sizes']), 1)
        self.assertEqual(len(self.director._formats['user_sizes']), 1)
        self.assertIsNotNone(self.director._formats['preview'])

        self.director.clear_formats()

        self.assertEqual(len(self.director._formats['sizes']), 0)
        self.assertEqual(len(self.director._formats['user_sizes']), 0)
        self.assertIsNone(self.director._formats['preview'])

    #
    # Cache Methods
    # ----------------------------------------------------------------

    def test_cache_methods(self):
        self.assertRaises(NotImplementedError, self.director.set_cache, key='#bad')
        self.assertRaises(NotImplementedError, self.director.disable_cache)

    # ----------------------------------------------------------------


if __name__ == '__main__':
    unittest.main()
