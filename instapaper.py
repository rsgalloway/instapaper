# ---------------------------------------------------------------------------------------------
# Copyright (c) 2013, Ryan Galloway (ryan@rsgalloway.com)
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

import os
import sys
import urllib2
import urlparse
import simplejson as json
import oauth2 as oauth
from lxml import etree
from urllib import urlencode

from HTMLParser import HTMLParser
from re import sub
from sys import stderr
from traceback import print_exc

__author__ = "Ryan Galloway <ryan@rsgalloway.com>"

__doc__ = """
An unofficial Python wrapper to the full Instapaper API.

http://www.instapaper.com/api/full
"""

_BASE_ = "https://www.instapaper.com"
_API_VERSION_ = "api/1"
_ACCESS_TOKEN_ = "oauth/access_token"
_ACCOUNT_ = "account/verify_credentials"
_BOOKMARKS_LIST_ = "bookmarks/list"
_BOOKMARKS_TEXT_ = "bookmarks/get_text"
_BOOKMARKS_STAR_ = "bookmarks/star"
_BOOKMARKS_UNSTAR_ = "bookmarks/unstar"
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
        'private_source': u''}

        """
        self.starred = (self.starred == '1') # convert to boolean

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
                self.__html = html
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

    def save(self):
        raise NotImplementedError

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
        _oauth = dict(urlparse.parse_qsl(content))
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
        user = json.loads(data)[0]
        if user.get("type") == "error":
                raise Exception(item.get("message"))
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
        items = json.loads(data)
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
        items = json.loads(data)
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

