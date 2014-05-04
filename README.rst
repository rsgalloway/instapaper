
Instapaper
==========

Unofficial full Instapaper API Python wrapper.


Installation
------------

Using easy install ::

    $ easy_install instapaper

Or from source ::

    $ git clone https://github.com/rsgalloway/instapaper.git
    $ cd instapaper
    $ python setup.py install


Basic Usage
-----------

Currently, only fetching existing bookmarks are supported.  ::

    >>> from instapaper import Instapaper as ipaper
    >>> i = ipaper(key, secret)
    >>> i.login(login, pw)
    >>> marks = i.bookmarks()

Get the html: ::

    >>> marks[0].html

Or the raw text: ::
    
    >>> marks[0].text

Save to a folder: ::

    >>> marks[0].move(folder_id=1234567)

Folders: ::

    >>> folders = i.folders()
    >>> for f in folders:
    ...     print f.folder_id, f.title


Playback
--------

Have a long commute home from work? Have your Instapaper bookmarks read back to you
using "utter" (pip install utter). You can even have them read back to you in a
differnet language, for example Italian: ::

    >>> import utter
    >>> for m in marks:
    ...     utter.play(m.text, target="it")


