import logging
import os
import re
import shutil
import subprocess
import tempfile
from functools import cached_property
from urllib.parse import urlparse

from mutagen.mp4 import MP4, MP4Cover

from .api import API
from .twspace import Twspace

DEFAULT_FNAME_FORMAT = "(%(creator_name)s)%(title)s-%(id)s"
MP4_COVER_FORMAT_MAP = {"jpg": MP4Cover.FORMAT_JPEG, "png": MP4Cover.FORMAT_PNG}


class TwspaceDL:
    """Downloader class for twitter spaces"""

    def __init__(self, space: Twspace, format_str: str) -> None:
        self.space = space
        self.format_str = format_str or DEFAULT_FNAME_FORMAT
        self._tempdir = ""

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
        media_key = space["media_key"]
        try:
            metadata = API.live_video_stream_api.status(media_key)
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
        """Get the URL containing the chunks filenames"""
        response = API.client.get(self.master_url)
        playlist_suffix = response.text.splitlines()[3]
        domain = urlparse(self.master_url).netloc
        playlist_url = f"https://{domain}{playlist_suffix}"
        return playlist_url

    @property
    def playlist_text(self) -> str:
        """Modify the chunks URL using the master one to be able to download"""
        playlist_text = API.client.get(self.playlist_url).text
        master_url_wo_file = re.sub(r"master_playlist\.m3u8.*", "", self.master_url)
        playlist_text = re.sub(r"(?=chunk)", master_url_wo_file, playlist_text)
        return playlist_text

    def write_playlist(self, save_dir: str = "./") -> None:
        """Write the modified playlist for external use"""
        filename = os.path.basename(self.filename) + ".m3u8"
        path = os.path.join(save_dir, filename)
        with open(path, "w", encoding="utf-8") as stream_io:
            stream_io.write(self.playlist_text)
        logging.debug("%(path)s written to disk", dict(path=path))

    def download(self) -> None:
        """Download a twitter space"""
        if not shutil.which("ffmpeg"):
            raise FileNotFoundError("ffmpeg not installed")
        space = self.space
        self._tempdir = tempfile.mkdtemp(dir=".")
        self.write_playlist(save_dir=self._tempdir)
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
        filename_m3u8 = os.path.join(self._tempdir, filename + ".m3u8")
        filename_old = os.path.join(self._tempdir, filename + ".m4a")
        cmd_old = cmd_base.copy()
        cmd_old.insert(1, "-protocol_whitelist")
        cmd_old.insert(2, "file,https,httpproxy,tls,tcp")
        cmd_old.insert(8, filename_m3u8)
        cmd_old.append(filename_old)
        logging.debug("Command for the old part: %s", " ".join(cmd_old))

        if state == "Running":
            filename_new = os.path.join(self._tempdir, filename + "_new.m4a")
            cmd_new = cmd_base.copy()
            cmd_new.insert(6, (self.dyn_url))
            cmd_new.append(filename_new)

            concat_fn = os.path.join(self._tempdir, "list.txt")
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

            logging.debug("Command for the new part: %s", " ".join(cmd_new))
            logging.debug("Command for the merge: %s", " ".join(cmd_final))
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
                raise RuntimeError(
                    " ".join(err.cmd)
                    + "\nThis might be a temporary error, retry in a few minutes"
                ) from err
            if os.path.dirname(self.filename):
                os.makedirs(os.path.dirname(self.filename), exist_ok=True)
            shutil.move(filename_old, self.filename + ".m4a")

        logging.info("Finished downloading")

    def embed_cover(self) -> None:
        """Embed the user profile image as the cover art"""
        cover_url = self.space["creator_profile_image_url"]
        cover_ext = cover_url.split(".")[-1]
        try:
            response = API.client.get(cover_url)
            if cover_format := MP4_COVER_FORMAT_MAP.get(cover_ext):
                meta = MP4(f"{self.filename}.m4a")
                meta.tags["covr"] = [
                    MP4Cover(response.content, imageformat=cover_format)
                ]
                meta.save()
            else:
                logging.error(f"Unsupported user profile image format: {cover_ext}")
        except RuntimeError:
            logging.error(f"Cannot download user profile image from URL: {cover_url}")
            raise

    def cleanup(self) -> None:
        if os.path.exists(self._tempdir):
            shutil.rmtree(self._tempdir)
