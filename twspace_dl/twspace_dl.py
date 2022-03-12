import logging
import os
import re
import shutil
import subprocess
import tempfile
from functools import cached_property
from urllib.parse import urlparse

import requests

from .twspace import Twspace

DEFAULT_FNAME_FORMAT = "(%(creator_name)s)%(title)s-%(id)s"


class TwspaceDL:
    """Downloader class for twitter spaces"""

    def __init__(self, space: Twspace, format_str: str) -> None:
        self.space = space
        self.format_str = format_str or DEFAULT_FNAME_FORMAT
        self.session = requests.Session()
        self._tmpdir: str

    @cached_property
    def filename(self) -> str:
        """Returns the formatted filename"""
        filename = self.space.format(self.format_str)
        return filename

    @cached_property
    def dyn_url(self) -> str:
        """Returns the dynamic url i.e. the url used by the browser"""
        space = self.space
        if space["state"] == "Ended" and not space["available_for_replay"]:
            logging.error(
                (
                    "Can't Download. Space has ended, can't retrieve master url. "
                    "You can provide it with -f URL if you have it."
                )
            )
            raise ValueError("Space Ended")
        headers = {
            "authorization": (
                "Bearer "
                "AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs"
                "=1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA"
            ),
            "cookie": "auth_token=",
        }
        media_key = space["media_key"]
        response = requests.get(
            "https://twitter.com/i/api/1.1/live_video_stream/status/" + media_key,
            headers=headers,
        )
        try:
            metadata = response.json()
        except Exception as err:
            raise RuntimeError("Space isn't available", space.source) from err
        dyn_url = metadata["source"]["location"]
        return dyn_url

    @cached_property
    def master_url(self) -> str:
        """Master URL for a space"""
        master_url = re.sub(
            r"(?<=/audio-space/).*", "master_playlist.m3u8", self.dyn_url
        )
        return master_url

    @property
    def playlist_url(self) -> str:
        """Get the URL containing the chunks filenames"""
        response = requests.get(self.master_url)
        playlist_suffix = response.text.splitlines()[3]
        domain = urlparse(self.master_url).netloc
        playlist_url = f"https://{domain}{playlist_suffix}"
        return playlist_url

    @property
    def playlist_text(self) -> str:
        """Modify the chunks URL using the master one to be able to download"""
        playlist_text = requests.get(self.playlist_url).text
        master_url_wo_file = re.sub(r"master_playlist\.m3u8.*", "", self.master_url)
        playlist_text = re.sub(r"(?=chunk)", master_url_wo_file, playlist_text)
        return playlist_text

    def write_playlist(self, save_dir: str = "./") -> None:
        """Write the modified playlist for external use"""
        filename = os.path.basename(self.filename) + ".m3u8"
        path = os.path.join(save_dir, filename)
        with open(path, "w", encoding="utf-8") as stream_io:
            stream_io.write(self.playlist_text)
        logging.info(f"{path} written to disk")

    def download(self) -> None:
        """Download a twitter space"""
        if not shutil.which("ffmpeg"):
            raise FileNotFoundError("ffmpeg not installed")
        space = self.space
        tempdir = self._tmpdir = tempfile.mkdtemp(dir=".")
        self.write_playlist(save_dir=tempdir)
        state = space["state"]

        cmd_base = [
            "ffmpeg",
            "-y",
            "-stats",
            "-v",
            "warning",
            "-i",
            "-c",
            "copy",
            "-metadata",
            f"title={space['title']}",
            "-metadata",
            f"artist={space['creator_name']}",
            "-metadata",
            f"episode_id={space['id']}",
        ]

        filename = os.path.basename(self.filename)
        filename_m3u8 = os.path.join(tempdir, filename + ".m3u8")
        filename_old = os.path.join(tempdir, filename + ".m4a")
        cmd_old = cmd_base.copy()
        cmd_old.insert(1, "-protocol_whitelist")
        cmd_old.insert(2, "file,https,tls,tcp")
        cmd_old.insert(8, filename_m3u8)
        cmd_old.append(filename_old)

        if state == "Running":
            filename_new = os.path.join(tempdir, filename + "_new.m4a")
            cmd_new = cmd_base.copy()
            cmd_new.insert(6, (self.dyn_url))
            cmd_new.append(filename_new)

            concat_fn = os.path.join(tempdir, "list.txt")
            with open(concat_fn, "w", encoding="utf-8") as list_io:
                list_io.write(
                    "file "
                    + f"'{os.path.abspath(os.path.join(os.getcwd(), filename_old))}'"
                    + "\n"
                    + "file "
                    + f"'{os.path.abspath(os.path.join(os.getcwd(), filename_new))}'"
                )

            cmd_final = cmd_base.copy()
            cmd_final.insert(1, "-f")
            cmd_final.insert(2, "concat")
            cmd_final.insert(3, "-safe")
            cmd_final.insert(4, "0")
            cmd_final.insert(10, concat_fn)
            cmd_final.append(self.filename + ".m4a")

            try:
                subprocess.run(cmd_new, check=True)
                subprocess.run(cmd_old, check=True)
                subprocess.run(cmd_final, check=True)
            except subprocess.CalledProcessError as err:
                raise RuntimeError(" ".join(err.cmd)) from err
        else:
            try:
                subprocess.run(cmd_old, check=True)
            except subprocess.CalledProcessError as err:
                raise RuntimeError(" ".join(err.cmd)) from err
            shutil.move(filename_old, self.filename + ".m4a")

        logging.info("Finished downloading")
