instapaper
==========

Unofficial full Instapaper API Python wrapper.

## Installation

The easiest way to install is with pip:

```shell
$ pip install -U instapaper
```

Or from source

```shell
$ git clone https://github.com/rsgalloway/instapaper.git
$ cd instapaper
$ pip install .
```

#### envstack

Environment variables can be managed in the instapaper.env files using
[envstack](https://github.com/rsgalloway/envstack):

```shell
$ pip install -U envstack
$ envstack instapaper -- python
>>> import instapaper
>>> instapaper._API_VERSION_
'api/1.2'
```

#### distman

If installing from source you can use [distman](https://github.com/rsgalloway/distman)
to install pyseq using the provided `dist.json` file:

```bash
$ distman [-d]
```

Using distman will deploy the targets defined in the `dist.json` file to the
root folder defined by `$DEPLOY_ROOT`, which can either be added to the
instapaper.env file or a default.env file.

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
