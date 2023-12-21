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
    <a href="https://github.com/HoloArchivists/twspace-dl/releases">
      <img src="https://img.shields.io/github/downloads/HoloArchivists/twspace-dl/total?label=DOWNLOADS%20%28GITHUB%29&amp;style=for-the-badge" alt="Github Releases DLs">
    </a>
  </p>
  <p>A python module to download twitter spaces.</p>
</div>

## Screensots

<details>
<summary>GUI</summary>

![general tab](https://user-images.githubusercontent.com/77058942/172580094-3663f86d-3ee2-48d0-9313-f4ed71f048aa.png)
![input tab](https://user-images.githubusercontent.com/77058942/172580476-bb34dce0-08b0-41f6-852b-b68d32532add.png)
![running tab](https://user-images.githubusercontent.com/77058942/172580589-fd6b05bd-f081-4c7a-ab05-0640abda00ce.png)
![success pop up](https://user-images.githubusercontent.com/77058942/172580861-18b3ac9f-88d2-44cf-8b5d-135990a78f77.png)

</details>

<details>
<summary>CLI</summary>

![help](https://user-images.githubusercontent.com/77058942/172581224-9b465f78-4894-456f-9b85-5b76ee9bbfca.png)
![running](https://user-images.githubusercontent.com/77058942/172581500-174834c5-6883-44f9-a0a7-610dbb2103e5.png)

</details>


## Requirements

- `ffmpeg` if not using portable binaries.
- A logged in user's cookies file exported from Twitter in the [Netscape format](https://curl.se/docs/http-cookies.html).

## Install

### GUI

Use this if you're not sure.

### From portable binaries

[Windows](https://github.com/HoloArchivists/twspace-dl/releases/latest/download/twspace-dl-GUI.exe)

### From source

```bash
pip install git+https://github.com/HoloArchivists/twspace-dl@gooey
```

### CLI

### From portable binaries

[Windows](https://github.com/HoloArchivists/twspace-dl/releases/latest/download/twspace-dl-CLI.exe)

### From PyPI

```bash
pip install twspace-dl
```

### From source

```bash
pip install git+https://github.com/HoloArchivists/twspace-dl
```

## Usage

```bash
twspace_dl -i space_url -c COOKIE_FILE
```

<details>
<summary>With binaries</summary>

### Windows

```powershell
.\twspace_dl.exe -i space_url -c COOKIE_FILE
```

</details>

## Features

Here's the output of the help option

```txt
usage: twspace_dl [-h] [-v] [-s] [-k] [-l] -c COOKIE_FILE
                  [-i SPACE_URL | -U USER_URL] [-d DYN_URL] [-f URL] [-M PATH]
                  [-o FORMAT_STR] [-m] [-p] [-u] [--write-url URL_OUTPUT] [-e]

Script designed to help download twitter spaces

options:
  -h, --help            show this help message and exit
  -v, --verbose
  -s, --skip-download
  -k, --keep-files
  -l, --log             create logfile
  -c COOKIE_FILE, --input-cookie-file COOKIE_FILE
                        cookies file in the Netscape format. The specs of the
                        Netscape cookies format can be found here:
                        https://curl.se/docs/http-cookies.html. The cookies
                        file is now required due to the Twitter API change
                        that prohibited guest user access to Twitter API
                        endpoints on 2023-07-01.

input:
  -i SPACE_URL, --input-url SPACE_URL
  -U USER_URL, --user-url USER_URL
  -d DYN_URL, --from-dynamic-url DYN_URL
                        use the dynamic url for the processes(useful for ended
                        spaces) example: https://prod-fastly-ap-northeast-
                        1.video.pscp.tv/Transcoding/v1/hls/zUUpEgiM0M18jCGxo2e
                        SZs99p49hfyFQr1l4cdze-Sp4T-
                        DQOMMoZpkbdyetgfwscfvvUkAdeF-
                        I5hPI4bGoYg/non_transcode/ap-northeast-1/periscope-
                        replay-direct-prod-ap-northeast-1-public/audio-
                        space/dynamic_playlist.m3u8?type=live
  -f URL, --from-master-url URL
                        use the master url for the processes(useful for ended
                        spaces) example: https://prod-fastly-ap-northeast-
                        1.video.pscp.tv/Transcoding/v1/hls/YRSsw6_P5xUZHMualK5
                        -ihvePR6o4QmoZVOBGicKvmkL_KB9IQYtxVqm3P_vpZ2HnFkoRfar4
                        _uJOjqC8OCo5A/non_transcode/ap-northeast-1/periscope-
                        replay-direct-prod-ap-northeast-1-public/audio-
                        space/master_playlist.m3u8
  -M PATH, --input-metadata PATH
                        use a metadata json file instead of input url (useful
                        for very old ended spaces)

output:
  -o FORMAT_STR, --output FORMAT_STR
  -m, --write-metadata  write the full metadata json to a file
  -p, --write-playlist  write the m3u8 used to download the stream(e.g. if you
                        want to use another downloader)
  -u, --url             display the master url
  --write-url URL_OUTPUT
                        write master url to file
  -e, --embed-cover     embed user avatar as cover art
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
%(creator_id)s
```

Example: `[%(creator_screen_name)s]-%(title)s|%(start_date)s`

## Known Errors

`Changing ID3 metadata in HLS audio elementary stream is not implemented....`

This is an error in ffmpeg that does not affect twspace_dl at all as far as I know.

## Service

To run as a systemd service please refer to https://github.com/HoloArchivists/twspace-dl/blob/main/SERVICE.md

## Docker

### Run once

```bash
docker run --rm -v .:/output holoarchivists/twspace-dl -i space_url
```

### Run as monitoring service

1. Download the `docker-compose.yml`, `.env`, `monitor.sh` files and put them in a folder named `twspace-dl`.
2. Edit `.env` and fill in the Twitter username you want to monitor.
3. Put a cookies file into the folder and named it `cookies.txt`.
4. `docker-compose up -d`
