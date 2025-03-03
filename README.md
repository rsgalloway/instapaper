instapaper
==========

Unofficial full Instapaper API Python wrapper.

## Installation

Using easy install

```shell
$ easy_install instapaper
```

Or from source

```shell
$ git clone https://github.com/rsgalloway/instapaper.git
$ cd instapaper
$ python setup.py install
```

## Basic Usage

Logging in:

```python
>>> from instapaper import Instapaper as ipaper
>>> i = ipaper(INSTAPAPER_KEY, INSTAPAPER_SECRET)
>>> i.login(email_address, password)
```

Getting bookmarks: ::

```python
>>> marks = i.bookmarks()
```

Get the html: ::

```python
>>> marks[0].html
```

Or the raw text: ::
    
```python
>>> marks[0].text
```

Folders: ::

```python
>>> folders = i.folders()
>>> for f in folders:
...     print f.folder_id, f.title
```

Move bookmark: ::

```python
>>> marks[0].move(f.folder_id)
```


## Playback

Have a long commute home from work? Have your Instapaper bookmarks read back to you
using "utter" (pip install utter). You can even have them read back to you in a
differnet language, for example Italian: ::

```python
>>> import utter
>>> for m in marks:
...     utter.play(m.text, target="it")
```
