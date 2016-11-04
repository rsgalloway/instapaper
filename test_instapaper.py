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
    username, __, password = secrets.authenticators('instapaper.com')
    return (username, password)


def app_credentials_from_netrc():
    secrets = netrc.netrc()
    app_key, __, app_secret = secrets.authenticators('api.instapaper.com')
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
