"""Script designed to help download twitter spaces"""
import argparse
import logging
import re
import sys
from urllib.parse import urlparse

import requests


def main():
    parser = argparse.ArgumentParser(
        description="Script designed to help download twitter spaces"
    )
    parser.add_argument("-i", "--id", type=str, metavar="SPACE_ID")
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("-w", "--write-metadata", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    response = requests.get("https://twitter.com/").text
    last_line = response.splitlines()[-1]
    guest_token = re.findall(r"(?<=gt\=)\d{19}", last_line)[0]
    logging.debug(guest_token)

    params = {
        "variables": '{"id":"'
        + args.id
        + '","isMetatagsQuery":false,"withSuperFollowsUserFields":true,"withUserResults":true,"withBirdwatchPivots":false,"withReactionsMetadata":false,"withReactionsPerspective":false,"withSuperFollowsTweetFields":true,"withReplays":true,"withScheduledSpaces":true}'
    }
    headers = {
        "authorization": "Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs=1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA",
        "x-guest-token": guest_token,
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
    except KeyError:
        logging.error(metadata)
        raise RuntimeError(metadata)

    title = metadata["data"]["audioSpace"]["metadata"]["title"]
    if args.write_metadata:
        with open(f"{title}-{args.id}.json", "w") as metadata_io:
            metadata_io.write(response.text)
            logging.info("written metadata to disk")
    if metadata["data"]["audioSpace"]["metadata"]["state"] == "Ended":
        logging.error("Space has ended")
        sys.exit(1)

    headers = {
        "authorization": "Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs=1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA",
        "cookie": "auth_token=",
    }
    response = requests.get(
        "https://twitter.com/i/api/1.1/live_video_stream/status/" + media_key,
        headers=headers,
    )
    metadata = response.json()
    dyn_url = metadata["source"]["location"]
    logging.debug(dyn_url)
    master_url = dyn_url.removesuffix("?type=live").replace("dynamic", "master")

    response = requests.get(master_url)
    playlist_suffix = response.text.splitlines()[3]
    domain = urlparse(master_url).netloc
    playlist_url = f"https://{domain}{playlist_suffix}"
    playlist_text = requests.get(playlist_url).text
    master_url_wo_file = master_url.removesuffix("master_playlist.m3u8")
    playlist_text = re.sub(r"(?=chunk)", master_url_wo_file, playlist_text)
    with open(f"{title}-{args.id}.m3u8", "w") as stream_io:
        stream_io.write(playlist_text)
    logging.info(f"{args.id}.m3u8 written to disk")
    return 0


if __name__ == "__main__":
    main()
