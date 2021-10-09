# Twspace-dl

A python script to download twitter space, only works on running spaces (for now).

## Usage

requires ffmpeg and the requests module
```bash
python twspace_dl/main.py space_id
```

## Features
Here's the output of the help option
```
usage: main.py [-h] [-v] [-m] [-w] [-u] [-s] [-k] SPACE_ID

Script designed to help download twitter spaces

positional arguments:
  SPACE_ID

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose
  -m, --write-metadata
  -w, --write-playlist  write the m3u8 used to download the stream
  -u, --url             display the final url
  -s, --skip-download
  -k, --keep-files
```
