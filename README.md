<!-- markdownlint-disable MD033 MD041 -->

<div align="center">
  <h1 id="twspace-dl">Twspace-dl</h1>
  <p>
    <a href="https://pypi.org/project/twspace-dl/">
      <img src="https://img.shields.io/pypi/v/twspace-dl?style=for-the-badge" alt="PyPI">
    </a>
    <a href="https://pypi.org/project/twspace-dl/">
      <img src="https://img.shields.io/pypi/dm/twspace-dl?label=DOWNLOADS%20%28PYPI%29&amp;style=for-the-badge" alt="PyPI DLs">
    </a>
    <a href="https://github.com/Ryu1845/twspace-dl/releases">
      <img src="https://img.shields.io/github/downloads/Ryu1845/twspace-dl/total?label=DOWNLOADS%20%28GITHUB%29&amp;style=for-the-badge" alt="Github Releases DLs">
    </a>
  </p>
  <p>A python module to download twitter spaces.</p>
</div>

## Requirements

ffmpeg

## Install

### From portable binaries

[Linux](https://github.com/Ryu1845/twspace-dl/releases/latest/download/twspace_dl.bin)

[Windows](https://github.com/Ryu1845/twspace-dl/releases/latest/download/twspace_dl.exe)

### From PyPI

```bash
pip install twspace-dl
```

### From source

```bash
pip install git+https://github.com/Ryu1845/twspace-dl
```

## Usage

```bash
twspace_dl -i space_url
```

<details>
<summary>With binaries</summary>

### Windows

```bash
.\twspace_dl.exe -i space_url
```

### Linux

```bash
./twspace_dl.bin -i space_url
```

</details>

## Features

Here's the output of the help option

```txt
usage: twspace_dl [-h] [-v] [-s] [-k] [--input-cookie-file COOKIE_FILE] [-i SPACE_URL | -U USER_URL] [-d DYN_URL] [-f URL] [-M PATH] [-o FORMAT_STR] [-m] [-p] [-u] [--write-url URL_OUTPUT] {login} ...

Script designed to help download twitter spaces

positional arguments:
  {login}               (EXPERIMENTAL) Login to your account using username and password

options:
  -h, --help            show this help message and exit
  -v, --verbose
  -s, --skip-download
  -k, --keep-files
  --input-cookie-file COOKIE_FILE

input:
  -i SPACE_URL, --input-url SPACE_URL
  -U USER_URL, --user-url USER_URL
  -d DYN_URL, --from-dynamic-url DYN_URL
                        use the dynamic url for the processes(useful for ended spaces) 
                        example: https://prod-fastly-ap-northeast-1.video.pscp.tv/Transcoding/v1/hls/
                        zUUpEgiM0M18jCGxo2eSZs99p49hfyFQr1l4cdze-Sp4T-DQOMMoZpkbdyetgfwscfvvUkAdeF-I5hPI4bGoYg/
                        non_transcode/ap-northeast-1/periscope-replay-direct-prod-ap-northeast-1-public/
                        audio-space/dynamic_playlist.m3u8?type=live
  -f URL, --from-master-url URL
                        use the master url for the processes(useful for ended spaces) 
                        example: https://prod-fastly-ap-northeast-1.video.pscp.tv/Transcoding/v1/hls/
                        YRSsw6_P5xUZHMualK5-ihvePR6o4QmoZVOBGicKvmkL_KB9IQYtxVqm3P_vpZ2HnFkoRfar4_uJOjqC8OCo5A/
                        non_transcode/ap-northeast-1/periscope-replay-direct-prod-ap-
                        northeast-1-public/audio-space/master_playlist.m3u8
  -M PATH, --input-metadata PATH
                        use a metadata json file instead of input url (useful for very old ended spaces)

output:
  -o FORMAT_STR, --output FORMAT_STR
  -m, --write-metadata  write the full metadata json to a file
  -p, --write-playlist  write the m3u8 used to download the stream(e.g. if you want to use another downloader)
  -u, --url             display the master url
  --write-url URL_OUTPUT
                        write master url to file
```
## Format

You can use the following identifiers for the formatting

```python
%(title)s
%(id)s
%(start_date)s
%(creator_name)s
%(creator_screen_name)s
%(url)s
```

Example: `[%(creator_screen_name)s]-%(title)s|%(start_date)s`

## Known Errors

`Changing ID3 metadata in HLS audio elementary stream is not implemented....`

This is an error in ffmpeg that does not affect twspace_dl at all as far as I know.

## Service 

To run as a systemd service please refer to https://github.com/Ryu1845/twspace-dl/blob/main/SERVICE.md

## Docker

### Run once

> Use ${pwd} in powershell, or $(pwd) in bash

```bash
docker run --rm -v ${pwd}:/output ryu1845/twspace-dl -i space_url
```

### Run as monitoring service

Using a cookie can help solve some problem with the twitter api. However, using one is not necessary.

#### Without cookie

1. Download the `docker-compose.yml`, `.env`, `monitor.sh` files and put them in a folder named `twspace-dl`.
2. Edit `.env` and fill in the Twitter username you want to monitor.
3. \[Optional] If you want to used a cookies file, put it into the folder and named it `cookies.txt`.
4. `docker-compose up -d`
