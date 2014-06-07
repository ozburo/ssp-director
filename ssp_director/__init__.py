# -*- coding: utf-8 -*-
"""
    SSP Director
    ~~~~~~~~~~~~

    Python client for Slideshow Pro's Director API.

    :license: MIT License, see LICENSE for more details.
    :documentation: See README.md for documentation.

"""

__version__ = '1.0'

try:
    from urllib.request import urlopen
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlopen, urlencode

import random
import json
import re

# --------------------------------------------------------------------
# Exceptions
# --------------------------------------------------------------------

class DirectorConnectionError(Exception):
    pass

class DirectorApiError(Exception):
    pass

class DirectorError(Exception):
    pass

# --------------------------------------------------------------------
# App Mixin
# --------------------------------------------------------------------

class AppMixin(object):

    def get_version(self):
        """ Returns the version of the API the Director install is running.

        """
        data = self._get('app_version')
        return data['version']

    def get_limits(self):
        """ Returns the upload limits for the Director install.

        """
        return self._get('app_limits')

    def get_totals(self):
        """ Returns the total number of objects uploaded to Director and
            also the aggregate file size of those files.

        """
        return self._get('app_totals')

# --------------------------------------------------------------------
# Gallery Mixin
# --------------------------------------------------------------------

class GalleryMixin(object):

    def get_galleries(self):
        """ Returns a list of all galleries along with their member albums. The content
            of the member albums is not returned. If you need the content, you should call
            `get_album` whilst looping through the gallery's albums.

        """
        data = self._get('get_gallery_list')
        return data['galleries']

    def get_gallery(self, gallery_id, limit=0, order='display', with_content=True):
        """ Returns a single gallery along with its member albums and content.

        :param limit:
            The number of member albums to return. Defaults to all.

        :param order:
            Using this parameter you can override the album order setting for the
            gallery. Options are 'display', 'created_on' and 'modified_on'.

        :param with_content:
            Whether or not to return the member albums' content.

        """
        if order not in ['display', 'created_on', 'modified_on']:
            raise ValueError("order can only be 'display', 'created_on' or 'modified_on'")

        options = {
            'gallery_id': int(gallery_id),
            'limit': int(limit),
            'order': str(order),
            'with_content': int(bool(with_content)),
            }
        return self._get('get_gallery', options)

# --------------------------------------------------------------------
# Album Mixin
# --------------------------------------------------------------------

class AlbumMixin(object):

    def get_albums(self, only_published=True, only_active=True, list_only=False,
                   only_smart=False, exclude_smart=False, tags=None, tags_exclusive=True):
        """ Return a list of all albums.

        :param only_published:
            Whether to return only published albums or all albums.

        :param only_active:
            Whether to return only active content or all content.

        :param list_only:
            Whether to return only a list of albums with no associated content.

        :param only_smart:
            Whether to return only smart albums.

        :param exclude_smart:
            Whether or not to exclude smart albums.

        :param tags:
            A tag (or list of tags) to filter the returned albums by tags that have
            been assigned to them.

        :param tags_exclusive:
            Whether or not albums must have all the tags given or only one of them.

        """
        if not tags:
            tags = []

        if not hasattr(tags, '__iter__'):
            tags = [tags]

        options = {
            'only_published': int(bool(only_published)),
            'only_active': int(bool(only_active)),
            'list_only': int(bool(list_only)),
            'only_smart': int(bool(only_smart)),
            'exclude_smart': int(bool(exclude_smart)),
            }

        if tags:
            options.update({'tags': ','.join(str(tag) for tag in tags),
                            'tags_exclusive': int(bool(tags_exclusive))})

        data = self._get('get_album_list', options)
        return data['albums']

    def get_album(self, album_id, only_active=True):
        """ Returns a single album along with its content.

        :param only_active:
            Whether to return all album content or just active content.

        """
        options = {
            'album_id': int(album_id),
            'only_active': int(bool(only_active)),
            }
        return self._get('get_album', options)

    def get_galleries_by_album(self, album_id, exclude=None):
        """ Retrieves the galleries that the provided album is a part of. Only gallery
            data is returned, no associated albums or their content are returned.

        :param exclude:
            An id (or list of ids) related to any gallery or galleries you wish to
            exclude from the results.

        """
        if not exclude:
            exclude = []

        if not hasattr(exclude, '__iter__'):
            exclude = [exclude]

        options = {
            'album_id': int(album_id),
            }

        if exclude:
            options.update({'exclude': ','.join(str(int(id)) for id in exclude)})

        data = self._get('get_associated_galleries', options)
        return data['galleries']

# --------------------------------------------------------------------
# Content Mixin
# --------------------------------------------------------------------

class ContentMixin(object):

    def get_contents(self, limit=0, only_images=False, only_active=True, sort_on='created_on',
                     sort_direction='desc', scope=None, scope_id=None, tags=None, tags_exclusive=True):
        """Return a list of all content in Director.

        :param limit:
            The number of images to return. Defaults to all.

        :param only_images:
            Whether to return all content (including videos) or only images.

        :param only_active:
            Whether to return only active images or all images.

        :param sort_on:
            How to sort the images. Options are 'created_on', 'captured_on',
            'modified_on', 'filename' and 'random'.

        :param sort_direction:
            Which direction to sort the content. Options are 'desc' or 'asc'.

        :param scope:
            The model type to use when filtering the results. Options are
            'gallery' and 'album'.

        :param scope_id:
            The id of the gallery or album to filter results by.

        :param tags:
            A tag (or list of tags) to filter the returned contents by tags that have
            been assigned to them.

        :param tags_exclusive:
            Whether or not contents must have all the tags given or only one of them.

        """
        if sort_on not in ['created_on', 'captured_on', 'modified_on', 'filename', 'random']:
            raise ValueError("sort_on can only be 'created_on', 'captured_on', 'modified_on', "
                             "'filename' or 'random'")

        if sort_direction not in ['desc', 'asc']:
            raise ValueError("sort_direction can only be 'desc' or 'asc'")

        if scope and scope not in ['gallery', 'album']:
            raise ValueError("scope can only be 'gallery' or 'album'")

        if not tags:
            tags = []

        if not hasattr(tags, '__iter__'):
            tags = [tags]

        options = {
            'limit': int(limit),
            'only_images': int(bool(only_images)),
            'only_active': int(bool(only_active)),
            'sort_on': str(sort_on),
            'sort_direction': str(sort_direction).upper(),
            }

        if sort_on == 'random':
            options.update({'buster': random.randint(1, 1000000)})

        if scope and scope_id:
            options.update({'scope': str(scope), 'scope_id': int(scope_id)})

        if tags:
            options.update({'tags': ','.join(str(tag) for tag in tags),
                            'tags_exclusive': int(bool(tags_exclusive))})

        data = self._get('get_content_list', options)
        return data['contents']

    get_images = get_contents

    def get_content(self, content_id):
        """ Returns a single piece of content.

        """
        options = {
            'content_id': int(content_id),
            }
        return self._get('get_content', options)

    get_image = get_content

# --------------------------------------------------------------------
# User Mixin
# --------------------------------------------------------------------

class UserMixin(object):

    def get_users(self, sort='name', scope=None, scope_id=None, scope_all=False):
        """ Return a list of all users.

        :param sort:
            Defines how the users are returned. Options are 'name' or 'activity'.

        :param scope:
            The model type to use when filtering the results. Options are
            'gallery' and 'album'.

        :param scope_id:
            The id of the gallery or album to filter results by.

        :param scope_all:
            Whether to return only users who have created content or any user
            who has created or updated content.

        """
        if sort not in ['name', 'activity']:
            raise ValueError("sort can only be 'name' or 'activity'")

        if scope and scope not in ['gallery', 'album']:
            raise ValueError("scope can only be 'gallery' or 'album'")

        options = {
            'sort': str(sort),
            }
        if scope and scope_id:
            options.update({'user_scope_model': str(scope), 'user_scope_id': int(scope_id),
                            'user_scope_all': int(bool(scope_all))})

        data = self._get('get_users', options)
        return data['users']

# --------------------------------------------------------------------
# Format Mixin
# --------------------------------------------------------------------

class FormatMixin(object):

    _formats = {'sizes': [], 'user_sizes': [], 'preview': None}

    def add_format(self, name, width, height, crop=True, quality=75, sharpening=True):
        self._formats['sizes'].append((str(name), int(width), int(height), int(bool(crop)),
                              int(quality), int(bool(sharpening))))

    def add_user_format(self, name, width, height, crop=True, quality=75, sharpening=True):
        self._formats['user_sizes'].append((str(name), int(width), int(height), int(bool(crop)),
                              int(quality), int(bool(sharpening))))

    def set_preview_format(self, width, height, crop=True, quality=75, sharpening=True):
        self._formats['preview'] = (int(width), int(height), int(bool(crop)), int(quality),
                                    int(bool(sharpening)))

    def clear_formats(self):
        self._formats = {'sizes': [], 'user_sizes': [], 'preview': None}

# --------------------------------------------------------------------
# Cache Mixin
# --------------------------------------------------------------------

class CacheMixin(object):

    def set_cache(self, key, expire=None):
        raise NotImplementedError()

    def disable_cache(self):
        raise NotImplementedError()

# --------------------------------------------------------------------
# Director
# --------------------------------------------------------------------

class Director(AppMixin, GalleryMixin, AlbumMixin, ContentMixin, UserMixin, FormatMixin, CacheMixin):

    def __init__(self, api_key, api_path):
        try:
            service, key = api_key.strip().split('-')
        except ValueError:
            raise ValueError("API key is invalid")

        if service not in ['local', 'hosted']:
            raise ValueError("API key is invalid")

        api_path = api_path.strip().rstrip('/').replace('http://', '')
        if service == 'local':
            api_path = '%s/index.php?' % api_path

        self._api_path = 'http://%s/api/' % api_path

    def _get(self, scope, options=None):
        """ Make http request call to Director API.

        """
        if not options:
            options = {}

        for i, format in enumerate(self._formats['sizes'], start=1):
            options.update({'size[%s]' % i: ','.join(map(str, format))})

        for i, format in enumerate(self._formats['user_sizes'], start=1):
            options.update({'user_size[%s]' % i: ','.join(map(str, format))})

        if self._formats['preview']:
            options.update({'preview': ','.join(map(str, self._formats['preview']))})

        endpoint = '%s%s' % (self._api_path, scope)
        queryparams = '?%s' % urlencode(options)
        url = '%s%s' % (endpoint, queryparams)

        try:
            request = urlopen(url)
        except IOError:
            raise DirectorConnectionError("Couldn't connect to url: %s" % url)
        else:
            if request.getcode() != 200:
                raise DirectorConnectionError("Endpoint could not be reached: %s" %
                                              endpoint)

        response = request.read()

        try:
            regex = re.compile(r'\\(?![/u"])')
            response = regex.sub(r'', response)
            response = json.loads(response)
        except ValueError as e:
            raise DirectorApiError("Received malformed JSON: %s" % e)
        else:
            if response['stat'] != 'ok':
                raise DirectorError(response['error'])

        return response['data']


