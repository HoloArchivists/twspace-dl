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
usage: main.py [-h] [-i SPACE_ID] [-f URL] [-v] [-m] [-w] [-u] [-s] [-k]

Script designed to help download twitter spaces

optional arguments:
  -h, --help            show this help message and exit
  -i SPACE_ID, --space-id SPACE_ID
  -f URL, --from-url URL
                        use the master url for the processes(useful for ended spaces)
  -v, --verbose
  -m, --write-metadata
  -w, --write-playlist  write the m3u8 used to download the stream
  -u, --url             display the master url
  -s, --skip-download
  -k, --keep-files
```
