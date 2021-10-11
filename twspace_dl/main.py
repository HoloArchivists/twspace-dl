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
    def __init__(self, url: str, threads: int):
        if not url:
            logging.warning("No space url given, file won't have any metadata")
            self.id = "no_id"
        else:
            space_id = re.findall(r"(?<=spaces/)\w*", url)[0]
            self.id = space_id
        self.threads = threads
        self.progress = 0
        self.total_segments: int
        self.title = ""

    @property
    def _guest_token(self) -> str:
        response = requests.get("https://twitter.com/").text
        last_line = response.splitlines()[-1]
        guest_token = re.findall(r"(?<=gt\=)\d{19}", last_line)[0]
        logging.debug(guest_token)
        return guest_token

    def write_metadata(self) -> None:
        metadata = str(self.metadata)
        with open(f"{self.title}-{self.id}.json", "w", encoding="utf-8") as metadata_io:
            metadata_io.write(metadata)
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
        self.title = metadata["data"]["audioSpace"]["metadata"]["title"]
        return metadata

    @cached_property
    def master_url(self) -> str:
        if self.metadata["data"]["audioSpace"]["metadata"]["state"] == "Ended":
            logging.error(
                (
                    "Can't Download. Space has ended, can't retrieve master url. "
                    "You can provide it with -f URL if you have it."
                )
            )
            raise ValueError
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
    def playlist_text(self) -> str:
        playlist_text = requests.get(self.playlist_url).text
        master_url_wo_file = self.master_url.removesuffix("master_playlist.m3u8")
        playlist_text = re.sub(r"(?=chunk)", master_url_wo_file, playlist_text)
        return playlist_text

    def write_playlist(self) -> None:
        with open(f"{self.title}-{self.id}.m3u8", "w", encoding="utf-8") as stream_io:
            stream_io.write(self.playlist_text)
        logging.info(f"{self.title}-{self.id}.m3u8 written to disk")

    def merge(self) -> None:
        with open(f"{self.title}-{self.id}-tmp.aac", "wb") as final_io:
            for chunk in os.listdir("tmp"):
                with open(os.path.join("tmp", chunk), "rb") as chunk_io:
                    shutil.copyfileobj(
                        chunk_io,
                        final_io,
                    )
        actual_metadata = self.metadata["data"]["audioSpace"]["metadata"]
        author = actual_metadata["creator_results"]["result"]["legacy"]["name"]
        command = [
            "ffmpeg",
            "-y",
            "-v",
            "warning",
            "-i",
            f"{self.title}-{self.id}-tmp.aac",
            "-c",
            "copy",
            "-metadata",
            f"title={self.title}",
            "-metadata",
            f"author={author}",
            "-metadata",
            f"episode_id={self.id}",
            f"./{self.title}-{self.id}.aac",
        ]
        subprocess.run(command, check=True)
        logging.info("finished merging")
        os.remove(f"{self.title}-{self.id}-tmp.aac")

    def _download(self, url: str) -> None:
        chunk = requests.get(url).content
        chunk_name = url.split("/")[-1]
        with open(f"tmp/{chunk_name}", "wb") as tmp_file:
            tmp_file.write(chunk)
        self.progress += 1
        print(f"{self.progress*100/self.total_segments}%", end="\r")

    def download(self) -> None:
        segments = re.findall("https.*", self.playlist_text)
        self.total_segments = len(segments)
        logging.info("Total segments: %s", self.total_segments)
        print()

        os.makedirs("tmp", exist_ok=True)
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            executor.map(self._download, segments, timeout=60)
        logging.info("Finished downloading")
        self.merge()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Script designed to help download twitter spaces"
    )
    parser.add_argument("-i", "--input-url", type=str, metavar="SPACE_URL")
    parser.add_argument(
        "-f",
        "--from-master-url",
        type=str,
        metavar="URL",
        help="use the master url for the processes(useful for ended spaces)",
    )
    parser.add_argument(
        "-t",
        "--threads",
        type=int,
        metavar="THREADS",
        help="number of threads to run the script with(default with max)",
        default=os.cpu_count(),
    )
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument(
        "-m",
        "--write-metadata",
        action="store_true",
        help="write the full metadata json to a file",
    )
    parser.add_argument(
        "-w",
        "--write-playlist",
        action="store_true",
        help=(
            "write the m3u8 used to download the stream"
            "(e.g. if you want to use another downloader)"
        ),
    )
    parser.add_argument(
        "-u", "--url", action="store_true", help="display the master url"
    )
    parser.add_argument("-s", "--skip-download", action="store_true")
    parser.add_argument("-k", "--keep-files", action="store_true")
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)
    args = parser.parse_args()
    if not args.input_url and not args.from_master_url:
        print("Either space url or master url should be provided")
        sys.exit(1)

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    twspace_dl = TwspaceDL(args.input_url, args.threads)
    if args.from_master_url:
        twspace_dl.master_url = args.from_master_url
    if args.write_metadata:
        twspace_dl.write_metadata()
    if args.url:
        print(twspace_dl.master_url)
    if args.write_playlist:
        twspace_dl.write_playlist()
    if not args.skip_download:
        try:
            twspace_dl.download()
        except KeyboardInterrupt:
            logging.info("Download Interrupted")
        finally:
            if not args.keep_files and os.path.exists("tmp"):
                shutil.rmtree("tmp")
