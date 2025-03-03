#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------------------------
# Copyright (c) 2013-2025, Ryan Galloway (ryan@rsgalloway.com)
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
# ---------

"""
Create .netrc file in HOME folder with content includes this:

machine instapaper.com
  login <username>
  password <password>
machine api.instapaper.com
  login <app_key>
  password <app_secret>

"""
import netrc
import instapaper


def credentials_from_netrc():
    secrets = netrc.netrc()
    username, __, password = secrets.authenticators("instapaper.com")
    return (username, password)


def app_credentials_from_netrc():
    secrets = netrc.netrc()
    app_key, __, app_secret = secrets.authenticators("api.instapaper.com")
    return (app_key, app_secret)


def test_login():
    instapaper_engine = instapaper.Instapaper(*app_credentials_from_netrc())
    instapaper_engine.login(*credentials_from_netrc())
    assert instapaper_engine.http is not None


def test_user():
    instapaper_engine = instapaper.Instapaper(*app_credentials_from_netrc())
    instapaper_engine.login(*credentials_from_netrc())
    user = instapaper_engine.user()
    assert user is not None


def test_bookmarks():
    instapaper_engine = instapaper.Instapaper(*app_credentials_from_netrc())
    instapaper_engine.login(*credentials_from_netrc())
    bookmarks = instapaper_engine.bookmarks()
    assert bookmarks is not None
