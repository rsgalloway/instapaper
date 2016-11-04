#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------------------------
# Copyright (c) 2013-2016, Ryan Galloway (ryan@rsgalloway.com)
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# - Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.
#
# - Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# - Neither the name of the software nor the names of its contributors
# may be used to endorse or promote products derived from this software
# without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# ---------------------------------------------------------------------------------------------
# docs and latest version available for download at
# http://github.com/rsgalloway/instapaper
# ---------------------------------------------------------------------------------------------

import sys
if sys.version_info > (3, 0):
    import urllib.parse as urlparse
    from urllib.parse import urlencode
    from html.parser import HTMLParser
else:
    import urlparse
    from urllib import urlencode
    from HTMLParser import HTMLParser


import json
import oauth2 as oauth

from re import sub
from sys import stderr
from traceback import print_exc

__author__ = "Ryan Galloway <ryan@rsgalloway.com>"

__doc__ = """
An unofficial Python wrapper to the full Instapaper API.

http://www.instapaper.com/api/full
"""

__todo__ = """
- refactor http requests to standalone function
"""

_BASE_ = "https://www.instapaper.com"
_API_VERSION_ = "api/1"
_ACCESS_TOKEN_ = "oauth/access_token"
_ACCOUNT_ = "account/verify_credentials"
_BOOKMARKS_LIST_ = "bookmarks/list"
_BOOKMARKS_TEXT_ = "bookmarks/get_text"
_BOOKMARKS_STAR_ = "bookmarks/star"
_BOOKMARKS_UNSTAR_ = "bookmarks/unstar"
_BOOKMARKS_ARCHIVE_ = "bookmarks/archive"
_BOOKMARKS_UNARCHIVE_ = "bookmarks/unarchive"
_BOOKMARKS_ADD_ = "bookmarks/add"
_BOOKMARKS_DELETE_ = "bookmarks/delete"
_BOOKMARKS_MOVE_ = "bookmarks/move"
_FOLDERS_ADD_ = "folders/add"
_FOLDERS_LIST_ = "folders/list"


class _DeHTMLParser(HTMLParser):

    def __init__(self):
        HTMLParser.__init__(self)
        self.__text = []

    def handle_data(self, data):
        text = data.strip()
        if len(text) > 0:
            text = sub('[ \t\r\n]+', ' ', text)
            self.__text.append(text + ' ')

    def handle_starttag(self, tag, attrs):
        if tag == 'p':
            self.__text.append('\n\n')
        elif tag == 'br':
            self.__text.append('\n')

    def handle_startendtag(self, tag, attrs):
        if tag == 'br':
            self.__text.append('\n\n')

    def text(self):
        return ''.join(self.__text).strip()


def dehtml(text):
    try:
        parser = _DeHTMLParser()
        if text:
            text = text.decode('UTF-8')
        else:
            return None
        parser.feed(text)
        parser.close()
        return parser.text()
    except:
        print_exc(file=stderr)
        return text


class Bookmark(object):

    def __init__(self, parent, params):
        self.parent = parent
        self.__text = None
        self.__html = None
        self.__dict__.update(params)
        """
        {'hash': '21iTZfCr',
        'description': u'',
        'parent': <instapaper.Instapaper object at 0x104055ad0>,
        'title': u'Let\u2019s Ignore Each Other Together',
        'url': 'https://medium.com/re-form/lets-ignore-each-other-together-d7cf46a8a8ad',
        '_Bookmark__html': None,
        'time': 1422657611,
        'progress_timestamp': 1422662236,
        'bookmark_id': 550386320,
        '_Bookmark__text': None,
        'progress': 0.0,
        'starred': '0',
        'type': 'bookmark',
        'content': u'',
        'private_source': u'',
        # is_private_from_source is used for adding a bookmark
        'is_private_from_source': u''}
        """
        try:
            self.starred = (self.starred == '1')  # convert to boolean
        except:
            self.starred = False

    def __str__(self):
        return '{}\n{}\n{}'.format(
            self.bookmark_id,
            self.title,
            self.url,
        )

    @property
    def html(self):
        if self.__html is None:
            response, html = self.parent.http.request(
                "/".join([_BASE_, _API_VERSION_, _BOOKMARKS_TEXT_]),
                method='POST',
                body=urlencode({
                    'bookmark_id': self.bookmark_id,
                }))
            if response.get("status") == "200":
                self.__html = html.decode('utf-8')
        return self.__html

    @property
    def text(self):
        if self.__text is None:
            self.__text = dehtml(self.html)
        return self.__text

    def star(self):
        response, html = self.parent.http.request(
            "/".join([_BASE_, _API_VERSION_, _BOOKMARKS_STAR_]),
            method='POST',
            body=urlencode({
                'bookmark_id': self.bookmark_id,
            }))
        if response.get("status") == "200":
            self.starred = True
            return True
        return False

    def unstar(self):
        response, html = self.parent.http.request(
            "/".join([_BASE_, _API_VERSION_, _BOOKMARKS_UNSTAR_]),
            method='POST',
            body=urlencode({
                'bookmark_id': self.bookmark_id,
            }))
        if response.get("status") == "200":
            self.starred = False
            return True
        return False

    def archive(self):
        response, html = self.parent.http.request(
            "/".join([_BASE_, _API_VERSION_, _BOOKMARKS_ARCHIVE_]),
            method='POST',
            body=urlencode({
                'bookmark_id': self.bookmark_id,
            }))
        if response.get("status") == "200":
            self.starred = True
            return True
        return False

    def unarchive(self):
        response, html = self.parent.http.request(
            "/".join([_BASE_, _API_VERSION_, _BOOKMARKS_UNARCHIVE_]),
            method='POST',
            body=urlencode({
                'bookmark_id': self.bookmark_id,
            }))
        if response.get("status") == "200":
            self.starred = False
            return True
        return False

    def delete(self):
        response, html = self.parent.http.request(
            "/".join([_BASE_, _API_VERSION_, _BOOKMARKS_DELETE_]),
            method='POST',
            body=urlencode({
                'bookmark_id': self.bookmark_id,
            }))
        if response.get("status") == "200":
            return True
        return False

    def save(self, folder_id=None):
        # add appropriate parameters to a dictionary for encoding
        encoded_values = {}
        try:
            if self.content:
                encoded_values['content'] = self.content
        except:
            pass

        try:
            if self.is_private_from_source:
                encoded_values['is_private_from_source'] = self.is_private_from_source
        except:
            pass

        try:
            if self.url:
                encoded_values['url'] = self.url
        except:
            pass

        try:
            if self.title:
                encoded_values['title'] = self.title
        except:
            pass

        try:
            if self.description:
                encoded_values['description'] = self.description
        except:
            pass

        try:
            if folder_id:
                encoded_values['folder_id'] = folder_id
        except:
            pass

        # send the http request
        response, html = self.parent.http.request(
            "/".join([_BASE_, _API_VERSION_, _BOOKMARKS_ADD_]),
            method='POST',
            body=urlencode(encoded_values))
        if response.get("status") == "200":
            self.__html = html
        return self.__html

    def move(self, folder_id):
        response, html = self.parent.http.request(
            "/".join([_BASE_, _API_VERSION_, _BOOKMARKS_MOVE_]),
            method='POST',
            body=urlencode({
                'bookmark_id': self.bookmark_id,
                'folder_id': folder_id
            }))
        if response.get("status") == "200":
            return True
        return False


class Instapaper(object):

    def __init__(self, oauthkey, oauthsec):
        self.consumer = oauth.Consumer(oauthkey, oauthsec)
        self.client = oauth.Client(self.consumer)
        self.token = None
        self.http = None

    def login(self, username, password):
        response, content = self.client.request(
            "/".join([_BASE_, _API_VERSION_, _ACCESS_TOKEN_]),
            "POST", urlencode({
                'x_auth_mode': 'client_auth',
                'x_auth_username': username,
                'x_auth_password': password}))
        _oauth = dict(urlparse.parse_qsl(content.decode('utf-8')))
        self.login_with_token(_oauth['oauth_token'], _oauth['oauth_token_secret'])

    def login_with_token(self, oauth_token, oauth_token_secret):
        """
        When you want to access a user's data using their existing token
        """
        self.token = oauth.Token(oauth_token, oauth_token_secret)
        self.http = oauth.Client(self.consumer, self.token)

    def user(self):
        response, data = self.http.request(
            "/".join([_BASE_, _API_VERSION_, _ACCOUNT_]),
            method='POST',
            body=None)
        user = json.loads(data.decode('utf-8'))[0]
        if user.get("type") == "error":
            raise Exception(data.get("message"))
        return user

    def bookmarks(self, folder="unread", limit=10, have=""):
        """
        folder_id: Optional. Possible values are unread (default),
                   starred, archive, or a folder_id value.
        limit: Optional. A number between 1 and 500, default 25.
        """
        response, data = self.http.request(
            "/".join([_BASE_, _API_VERSION_, _BOOKMARKS_LIST_]),
            method='POST',
            body=urlencode({
                'folder_id': folder,
                'limit': limit,
                'have': have}))
        marks = []
        items = json.loads(data.decode('utf-8'))
        for item in items:
            if item.get("type") == "error":
                raise Exception(item.get("message"))
            elif item.get("type") == "bookmark":
                marks.append(Bookmark(self, item))
        return marks

    def folders(self):
        response, data = self.http.request(
            "/".join([_BASE_, _API_VERSION_, _FOLDERS_LIST_]),
            method='POST',
            body=urlencode({}))
        folders = []
        items = json.loads(data.decode('utf-8'))
        for item in items:
            folders.append(item)
        return folders

    def create_folder(self, title):
        """
        title: Required.  Title of the folder.
        """
        response, data = self.http.request(
            "/".join([_BASE_, _API_VERSION_, _FOLDERS_ADD_]),
            method='POST',
            body=urlencode({
                'title': title}))
        if response.get("status") == "200":
            return True
        raise Exception(response)
