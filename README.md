# Twspace-dl

A python script to download twitter space.

## Downloads

[Linux](https://github.com/Ryu1845/twspace-dl/releases/latest/download/twspace_dl.bin)

[Windows](https://github.com/Ryu1845/twspace-dl/releases/latest/download/twspace_dl.exe)

## Usage

The script downloads from the beginning to the moment you started the script.

### Linux
```bash
./twspace_dl.bin -i space_url --wait 15
```

### Windows
```batch
.\twspace_dl.exe -i space_url --wait 15
```

## Features
Here's the output of the help option
```
usage: main.py [-h] [-i SPACE_URL] [-w TIME] [-f URL] [-t THREADS] [-v] [-m] [-p] [-u] [-s] [-k]

Script designed to help download twitter spaces

optional arguments:
  -h, --help            show this help message and exit
  -i SPACE_URL, --input-url SPACE_URL
  -w TIME, --wait TIME  Wait for a space to end to download it
  -f URL, --from-master-url URL
                        use the master url for the processes(useful for ended spaces)
  -t THREADS, --threads THREADS
                        number of threads to run the script with(default with max)
  -v, --verbose
  -m, --write-metadata  write the full metadata json to a file
  -p, --write-playlist  write the m3u8 used to download the stream(e.g. if you want to use another downloader)
  -u, --url             display the master url
  -s, --skip-download
  -k, --keep-files
```

