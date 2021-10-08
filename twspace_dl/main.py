import argparse
import re
from urllib.parse import urlparse

import requests


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--id", type=str)
    args = parser.parse_args()

    params = {
        "variables": '{"id":"'
        + args.id
        + '","isMetatagsQuery":false,"withSuperFollowsUserFields":true,"withUserResults":true,"withBirdwatchPivots":false,"withReactionsMetadata":false,"withReactionsPerspective":false,"withSuperFollowsTweetFields":true,"withReplays":false,"withScheduledSpaces":true}'
    }
    headers = {
        "authorization": "Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs=1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA",
        "x-guest-token": "1446600991122632705",
    }
    response = requests.get(
        "https://twitter.com/i/api/graphql/jyQ0_DEMZHeoluCgHJ-U5Q/AudioSpaceById",
        params=params,
        headers=headers,
    )
    metadata = response.json()
    media_key = metadata["data"]["audioSpace"]["metadata"]["media_key"]
    print(f"{media_key=}")

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
    print(f"{dyn_url=}")
    master_url = dyn_url.removesuffix("?type=live").replace("dynamic", "master")
    print(f"{master_url=}")

    response = requests.get(master_url)
    playlist_suffix = response.text.splitlines()[3]
    domain = urlparse(master_url).netloc
    playlist_url = f"https://{domain}{playlist_suffix}"
    playlist_text = requests.get(playlist_url).text
    master_url_wo_file = master_url.removesuffix("master_playlist.m3u8")
    playlist_text = re.sub(r"(?=chunk)", master_url_wo_file, playlist_text)
    with open(args.id + ".m3u8", "x") as stream_io:
        stream_io.write(playlist_text)
    print(f"{args.id}.m3u8 written to disk")


if __name__ == "__main__":
    main()
