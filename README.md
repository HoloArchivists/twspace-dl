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
  <p>A python script to download twitter spaces.</p>
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
git clone --depth 1 https://github.com/Ryu1845/twspace-dl
cd twspace-dl
pip install .
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
usage: twspace_dl [-h] [-t THREADS] [-v] [-s] [-k] [-i SPACE_URL] [-U USER_URL] [-M PATH] [-d DYN_URL] [-f URL]
                  [-o FORMAT_STR] [-m] [-p] [-u]

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
  -U USER_URL, --user-url USER_URL
  -M PATH, --input-metadata PATH
                        use a metadata json file instead of input url (useful for very old ended spaces)
  -d DYN_URL, --from-dynamic-url DYN_URL
                        use the dynamic url for the processes(useful for ended spaces) example: https://prod-
                        fastly-ap-
                        northeast-1.video.pscp.tv/Transcoding/v1/hls/zUUpEgiM0M18jCGxo2eSZs99p49hfyFQr1l4cdze-
                        Sp4T-DQOMMoZpkbdyetgfwscfvvUkAdeF-I5hPI4bGoYg/non_transcode/ap-northeast-1/periscope-
                        replay-direct-prod-ap-northeast-1-public/audio-space/dynamic_playlist.m3u8?type=live
  -f URL, --from-master-url URL
                        use the master url for the processes(useful for ended spaces) example: https://prod-
                        fastly-ap-northeast-1.video.pscp.tv/Transcoding/v1/hls/YRSsw6_P5xUZHMualK5-ihvePR6o4QmoZV
                        OBGicKvmkL_KB9IQYtxVqm3P_vpZ2HnFkoRfar4_uJOjqC8OCo5A/non_transcode/ap-
                        northeast-1/periscope-replay-direct-prod-ap-northeast-1-public/audio-
                        space/master_playlist.m3u8

output:
  -o FORMAT_STR, --output FORMAT_STR
  -m, --write-metadata  write the full metadata json to a file
  -p, --write-playlist  write the m3u8 used to download the stream(e.g. if you want to use another downloader)
  -u, --url             display the master url
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

Example: `[%(creator_screen_name)s]-%(title)s|%(start_date)s`

## Service

There's an example service file [there](https://github.com/Ryu1845/twspace-dl/blob/main/twspace-dl@.service)
You'll have to modify different stuff depending on how you installed or not the script.

I'd be very grateful if someone made a PR with a bash script automating those ;)

### Cloned Repository

In that case, you'll have to modify the `WorkingDirectory` to where you cloned the repo.

### Pip

1. Change `WorkingDirectory` to where you want the spaces to be downloaded.
2. Find where your executable is by running `which twspace_dl` in your terminal.
3. Change the `/usr/bin/python twspace_dl` part to the path of your executable.

Now to install the service, you can either install it as a user service(recommended if on your personal desktop), or as a normal service.

### User

1. Copy the file you modified earlier to `~/.config/systemd/user`(create the systemd directory if it doesn't exist).
2. run

``` bash
systemctl --user daemon-reload
systemctl --user start twspace-dl@USER_ID.service
```

`USER_ID` is the part after `https://twitter.com/` in the url of a twitter profile (i.e `https://twitter.com/USER_ID`)

To keep it working after restarts run:

``` bash
systemctl --user enable twspace-dl@USER_ID.service
```

### System

1. Copy the file you modified earlier to `/etc/systemd/system`.
2. run

``` bash
sudo systemctl daemon-reload
sudo systemctl start twspace-dl@USER_ID.service
```

`USER_ID` is the part after `https://twitter.com/` in the url of a twitter profile (i.e `https://twitter.com/USER_ID`)

To keep it working after restarts run:

``` bash
sudo systemctl enable twspace-dl@USER_ID.service
```
