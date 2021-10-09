"""Script designed to help download twitter spaces"""
import argparse
import logging
import os
import re
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from functools import cached_property
from urllib.parse import urlparse

import requests


class TwspaceDL:
    def __init__(self, space_id: str):
        self.id = space_id
        self.progress = 0
        self.total_segments: int
        self.title: str

    @property
    def _guest_token(self) -> str:
        response = requests.get("https://twitter.com/").text
        last_line = response.splitlines()[-1]
        guest_token = re.findall(r"(?<=gt\=)\d{19}", last_line)[0]
        logging.debug(guest_token)
        return guest_token

    def write_metadata(self) -> None:
        with open(f"{self.title}-{self.id}.json", "w", encoding="utf-8") as metadata_io:
            metadata_io.write(str(self.metadata))
            logging.info(f"{self.title}-{self.id}.json written to disk")

    @cached_property
    def metadata(self) -> dict:
        params = {
            "variables": (
                "{"
                f'"id":"{self.id}",'
                '"isMetatagsQuery":false,'
                '"withSuperFollowsUserFields":true,'
                '"withUserResults":true,'
                '"withBirdwatchPivots":false,'
                '"withReactionsMetadata":false,'
                '"withReactionsPerspective":false,'
                '"withSuperFollowsTweetFields":true,'
                '"withReplays":true,'
                '"withScheduledSpaces":true'
                "}"
            )
        }
        headers = {
            "authorization": (
                "Bearer "
                "AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs"
                "=1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA"
            ),
            "x-guest-token": self._guest_token,
        }
        response = requests.get(
            "https://twitter.com/i/api/graphql/jyQ0_DEMZHeoluCgHJ-U5Q/AudioSpaceById",
            params=params,
            headers=headers,
        )
        metadata = response.json()
        try:
            media_key = metadata["data"]["audioSpace"]["metadata"]["media_key"]
            logging.debug(media_key)
        except KeyError as error:
            logging.error(metadata)
            raise RuntimeError(metadata) from error
        self.title = (
            metadata["data"]["audioSpace"]["metadata"]["title"]
            if "title" in metadata["data"]["audioSpace"]["metadata"].keys()
            else ""
        )
        if metadata["data"]["audioSpace"]["metadata"]["state"] == "Ended":
            logging.error("Space has ended")
            sys.exit(1)
        return metadata

    @cached_property
    def master_url(self) -> str:
        headers = {
            "authorization": (
                "Bearer "
                "AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs"
                "=1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA"
            ),
            "cookie": "auth_token=",
        }
        media_key = self.metadata["data"]["audioSpace"]["metadata"]["media_key"]
        response = requests.get(
            "https://twitter.com/i/api/1.1/live_video_stream/status/" + media_key,
            headers=headers,
        )
        metadata = response.json()
        dyn_url = metadata["source"]["location"]
        logging.debug(dyn_url)
        master_url = dyn_url.removesuffix("?type=live").replace("dynamic", "master")
        return master_url

    @cached_property
    def playlist_url(self) -> str:
        response = requests.get(self.master_url)
        playlist_suffix = response.text.splitlines()[3]
        domain = urlparse(self.master_url).netloc
        playlist_url = f"https://{domain}{playlist_suffix}"
        return playlist_url

    @cached_property
    def playlist_text(self):
        playlist_text = requests.get(self.playlist_url).text
        master_url_wo_file = self.master_url.removesuffix("master_playlist.m3u8")
        playlist_text = re.sub(r"(?=chunk)", master_url_wo_file, playlist_text)
        return playlist_text

    def write_playlist(self) -> None:
        with open(f"{self.title}-{self.id}.m3u8", "w", encoding="utf-8") as stream_io:
            stream_io.write(self.playlist_text)
        logging.info(f"{self.title}-{self.id}.m3u8 written to disk")

    def merge(self):
        with open(f"{self.title}-{self.id}-tmp.aac", "wb") as final_io:
            for chunk in os.listdir("tmp"):
                with open(os.path.join("tmp", chunk), "rb") as chunk_io:
                    shutil.copyfileobj(
                        chunk_io,
                        final_io,
                    )
        command = [
            "ffmpeg",
            "-y",
            "-v",
            "warning",
            "-i",
            f"{self.title}-{self.id}-tmp.aac",
            "-c",
            "copy",
            f"{self.title}-{self.id}.aac",
        ]
        subprocess.run(command, check=True)
        logging.info("finished merging")
        os.remove(f"{self.title}-{self.id}-tmp.aac")

    def _download(self, url):
        chunk = requests.get(url).content
        chunk_name = url.split("/")[-1]
        with open(f"tmp/{chunk_name}", "wb") as tmp_file:
            tmp_file.write(chunk)
        self.progress += 1
        print(f"{self.progress*100/self.total_segments}%", end="\r")

    def download(self):
        segments = re.findall("https.*", self.playlist_text)
        self.total_segments = len(segments)
        logging.info("Total segments: %s", self.total_segments)
        print()

        os.makedirs("tmp", exist_ok=True)
        with ThreadPoolExecutor(max_workers=12) as executor:
            executor.map(self._download, segments, timeout=60)
        logging.info("Finished downloading")
        self.merge()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Script designed to help download twitter spaces"
    )
    parser.add_argument("-i", "--id", type=str, metavar="SPACE_ID")
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("-w", "--write-metadata", action="store_true")
    parser.add_argument(
        "-u", "--url", action="store_true", help="display the master url"
    )
    parser.add_argument("-s", "--skip-download", action="store_true")
    parser.add_argument("-k", "--keep-files", action="store_true")
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)
    args = parser.parse_args()
    if not args.id:
        print("ID is required")
        sys.exit(1)

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    twspace_dl = TwspaceDL(args.id)
    if args.write_metadata:
        twspace_dl.write_metadata()
    if args.url:
        print(twspace_dl.master_url)
    if not args.skip_download:
        try:
            twspace_dl.download()
        except KeyboardInterrupt:
            logging.info("Download Interrupted")
        finally:
            if not args.keep_files and os.path.exists("tmp"):
                shutil.rmtree("tmp")
