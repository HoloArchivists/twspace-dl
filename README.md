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
usage: main.py [-h] [-i SPACE_URL] [-f URL] [-t THREADS] [-v] [-m] [-w] [-u] [-s] [-k]

Script designed to help download twitter spaces

optional arguments:
  -h, --help            show this help message and exit
  -i SPACE_URL, --input-url SPACE_URL
  -f URL, --from-master-url URL
                        use the master url for the processes(useful for ended spaces)
  -t THREADS, --threads THREADS
                        number of threads to run the script with(default with max)
  -v, --verbose
  -m, --write-metadata  write the full metadata json to a file
  -w, --write-playlist  write the m3u8 used to download the stream(e.g. if you want to use another downloader)
  -u, --url             display the master url
  -s, --skip-download
  -k, --keep-files
```
