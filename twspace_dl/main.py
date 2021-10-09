"""Script designed to help download twitter spaces"""
import argparse
import logging
import re
import sys
from urllib.parse import urlparse

import requests


class TwspaceDL:
    def __init__(self, space_id, write_metadata):
        self.id = space_id
        self.write_metadata = write_metadata
        self.guest_token = self.get_guest_token()
        self.media_key = self.get_metadata()
        self.master_url = self.get_master_url()

    @staticmethod
    def get_guest_token():
        response = requests.get("https://twitter.com/").text
        last_line = response.splitlines()[-1]
        guest_token = re.findall(r"(?<=gt\=)\d{19}", last_line)[0]
        logging.debug(guest_token)
        return guest_token

    def get_metadata(self):
        params = {
            "variables": '{"id":"'
            + self.id
            + '","isMetatagsQuery":false,"withSuperFollowsUserFields":true,"withUserResults":true,"withBirdwatchPivots":false,"withReactionsMetadata":false,"withReactionsPerspective":false,"withSuperFollowsTweetFields":true,"withReplays":true,"withScheduledSpaces":true}'
        }
        headers = {
            "authorization": "Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs=1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA",
            "x-guest-token": self.guest_token,
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
        if self.write_metadata:
            with open(
                f"{self.title}-{self.id}.json", "w", encoding="utf-8"
            ) as metadata_io:
                metadata_io.write(response.text)
                logging.info(f"{self.title}-{self.id}.json written to disk")
        if metadata["data"]["audioSpace"]["metadata"]["state"] == "Ended":
            logging.error("Space has ended")
            sys.exit(1)
        return media_key

    def get_master_url(self):
        headers = {
            "authorization": "Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs=1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA",
            "cookie": "auth_token=",
        }
        response = requests.get(
            "https://twitter.com/i/api/1.1/live_video_stream/status/" + self.media_key,
            headers=headers,
        )
        metadata = response.json()
        dyn_url = metadata["source"]["location"]
        logging.debug(dyn_url)
        master_url = dyn_url.removesuffix("?type=live").replace("dynamic", "master")
        return master_url

    def write_playlist(self):
        response = requests.get(self.master_url)
        playlist_suffix = response.text.splitlines()[3]
        domain = urlparse(self.master_url).netloc
        playlist_url = f"https://{domain}{playlist_suffix}"
        playlist_text = requests.get(playlist_url).text
        master_url_wo_file = self.master_url.removesuffix("master_playlist.m3u8")
        playlist_text = re.sub(r"(?=chunk)", master_url_wo_file, playlist_text)
        with open(f"{self.title}-{self.id}.m3u8", "w", encoding="utf-8") as stream_io:
            stream_io.write(playlist_text)
        logging.info(f"{self.id}.m3u8 written to disk")
        return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Script designed to help download twitter spaces"
    )
    parser.add_argument("-i", "--id", type=str, metavar="SPACE_ID")
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("-w", "--write-metadata", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    TwspaceDL(args.id, args.write_metadata).write_playlist()
