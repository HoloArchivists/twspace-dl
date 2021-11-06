# Twspace-dl

A python script to download twitter space.

## Install

### From source
```bash
git clone --depth 1 https://github.com/Ryu1845/twspace-dl
cd twspace-dl
pip install .
```

### From PyPI
```bash
pip install twspace-dl
```

## Usage
```bash
twspace_dl -i space_url
```

## Features
Here's the output of the help option
```
usage: twspace_dl [-h] [-t THREADS] [-v] [-s] [-k] [-i SPACE_URL] [-d DYN_URL] [-f URL] [-o FORMAT_STR] [-m] [-p] [-u]

Script designed to help download twitter spaces

optional arguments:
  -h, --help            show this help message and exit
  -t THREADS, --threads THREADS
                        number of threads to run the script with(default with max)
  -v, --verbose
  -s, --skip-download
  -k, --keep-files

input:
  -i SPACE_URL, --input-url SPACE_URL
  -d DYN_URL, --from-dynamic-url DYN_URL
                        use the master url for the processes(useful for ended spaces)
  -f URL, --from-master-url URL
                        use the master url for the processes(useful for ended spaces)

output:
  -o FORMAT_STR, --output FORMAT_STR
  -m, --write-metadata  write the full metadata json to a file
  -p, --write-playlist  write the m3u8 used to download the stream(e.g. if you want to use another downloader)
  -u, --url             display the master url
```

## Format
You can use the following identifiers for the formatting
```
%(title)s
%(id)s
%(start_date)s
%(creator_name)s
%(creator_screen_name)s
%(url)s
```
Example: `[%(creator_screen_name)s]-%(title)s|%(start_date)s`
