"""Provide an interface with twitter spaces"""
import json
import logging
import os
import re
from collections import defaultdict
from datetime import datetime

import requests
from requests.exceptions import JSONDecodeError

from . import twitter


class Twspace(dict):
    """Downloader class for twitter spaces"""

    def __init__(self, metadata: dict) -> None:
        dict.__init__(
            self,
            {
                "id": "",
                "url": "",
                "title": "",
                "creator_name": "",
                "creator_id": "",
                "creator_screen_name": "",
                "start_date": "",
                "start_year": "",
                "start_month": "",
                "start_day": "",
                "state": "",
                "available_for_replay": "",
                "media_key": "",
            },
        )
        if metadata:
            root = defaultdict(str, metadata["data"]["audioSpace"]["metadata"])
            creator_info = root["creator_results"]["result"]["legacy"]  # type: ignore

            self.source = metadata
            self.root = root
            self["id"] = root["rest_id"]
            self["url"] = "https://twitter.com/i/spaces/" + self["id"]
            self["title"] = root["title"]
            self["creator_name"] = creator_info["name"]  # type: ignore
            self["creator_screen_name"] = creator_info["screen_name"]  # type: ignore
            try:
                start_at = datetime.fromtimestamp(
                    int(root["started_at"]) / 1000
                )
            except ValueError as err:
                sched_start = datetime.fromtimestamp(
                    int(root["scheduled_start"]) / 1000
                ).strftime("%Y-%m-%d %H:%M:%S")
                raise ValueError(
                    f"Space should start at {sched_start}, try again later"
                ) from err
            self["start_date"] = start_at.strftime("%Y-%m-%d")
            self["start_year"] = start_at.strftime("%Y")
            self["start_month"] = start_at.strftime("%m")
            self["start_day"] = start_at.strftime("%d")
            self["state"] = root["state"]
            self["available_for_replay"] = root["is_space_available_for_replay"]
            self["media_key"] = root["media_key"]
            self["creator_id"] = twitter.user_id(
                "https://twitter.com/" + creator_info["screen_name"]
            )

    @staticmethod
    def _metadata(space_id) -> dict:
        params = {
            "variables": (
                "{"
                f'"id":"{space_id}",'
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
            "x-guest-token": twitter.guest_token(),
        }
        response = requests.get(
            "https://twitter.com/i/api/graphql/jyQ0_DEMZHeoluCgHJ-U5Q/AudioSpaceById",
            params=params,
            headers=headers,
        )
        metadata = response.json()
        try:
            media_key = metadata["data"]["audioSpace"]["metadata"]["media_key"]
            logging.debug("Media Key: %s", media_key)
        except KeyError as error:
            logging.error(metadata)
            raise ValueError("Media Key not available.\nUser is not live") from error
        return metadata

    # https://gist.github.com/dbr/256270
    @staticmethod
    def sterilize_fn(value: str) -> str:
        """
        Takes a string and makes it into a valid filename.
        """

        # Treat extension seperatly
        value, extension = os.path.splitext(value)

        # Remove null byte
        value = value.replace("\0", "")

        # If the filename starts with a . prepend it with an underscore, so it
        # doesn't become hidden
        if value.startswith("."):
            value = "_" + value

        # platform.system docs say it could also return "Windows" or "Java".
        # Failsafe and use Windows sanitisation for Java, as it could be any
        # operating system.
        blacklist = r"\/:*?\"<>|"

        # Replace every blacklisted character with a underscore
        value = re.sub("[%s]" % re.escape(blacklist), "_", value)

        # Remove any trailing whitespace
        value = value.strip()

        # There are a bunch of filenames that are not allowed on Windows.
        # As with character blacklist, treat non Darwin/Linux platforms as Windows
        invalid_filenames = [
            "CON",
            "PRN",
            "AUX",
            "NUL",
            "COM1",
            "COM2",
            "COM3",
            "COM4",
            "COM5",
            "COM6",
            "COM7",
            "COM8",
            "COM9",
            "LPT1",
            "LPT2",
            "LPT3",
            "LPT4",
            "LPT5",
            "LPT6",
            "LPT7",
            "LPT8",
            "LPT9",
        ]
        if value in invalid_filenames:
            value = "_" + value

        return value + extension

    def format(self, format_str: str) -> str:
        """Use metadata to fill in the fields in format str"""
        actual_format_str = os.path.basename(format_str)
        abs_dir = os.path.dirname(format_str) % self
        basename = self.sterilize_fn(actual_format_str % self)
        return os.path.join(abs_dir, basename)

    @classmethod
    def from_space_url(cls, url: str):
        """Create a Twspace instance from a space url"""
        try:
            space_id = re.findall(r"(?<=spaces/)\w*", url)[0]
        except IndexError as err:
            raise ValueError(
                (
                    "Input URL is not valid.\n"
                    "The URL format should 'https://twitter.com/i/spaces/<space_id>'"
                )
            ) from err
        return cls(cls._metadata(space_id))

    @classmethod
    def from_user_tweets(cls, url: str):
        """Create a Twspace instance from the first space
        found in the 20 last user tweets"""
        user_id = twitter.user_id(url)
        headers = {
            "authorization": (
                "Bearer "
                "AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs"
                "=1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA"
            ),
            "x-guest-token": twitter.guest_token(),
        }
        params = {
            "variables": (
                "{"
                f'"userId":"{user_id}",'
                '"count":20,'
                '"withTweetQuoteCount":true,'
                '"includePromotedContent":true,'
                '"withQuickPromoteEligibilityTweetFields":false,'
                '"withSuperFollowsUserFields":true,'
                '"withUserResults":true,'
                '"withNftAvatar":false,'
                '"withBirdwatchPivots":false,'
                '"withReactionsMetadata":false,'
                '"withReactionsPerspective":false,'
                '"withSuperFollowsTweetFields":true,'
                '"withVoice":true}'
            )
        }
        response = requests.get(
            "https://twitter.com/i/api/graphql/jpCmlX6UgnPEZJknGKbmZA/UserTweets",
            params=params,
            headers=headers,
        )
        tweets = response.text

        try:
            space_id = re.findall(r"(?<=https://twitter.com/i/spaces/)\w*", tweets)[0]
        except (IndexError, json.JSONDecodeError) as err:
            raise RuntimeError(
                "User hasn't tweeted a space, retry with cookies"
            ) from err
        return cls(cls._metadata(space_id))

    @classmethod
    def from_user_avatar(cls, user_url, auth_token):
        """Create a Twspace instance from a twitter user's ongoing space"""
        headers = {
            "authorization": (
                "Bearer "
                "AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs"
                "=1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA"
            ),
            "cookie": f"auth_token={auth_token};",
        }
        user_id = twitter.user_id(user_url)
        params = {"user_ids": user_id, "only_spaces": "true"}
        avatar_content_res = requests.get(
            "https://twitter.com/i/api/fleets/v1/avatar_content",
            params=params,
            headers=headers,
        )
        if avatar_content_res.ok:
            avatar_content = avatar_content_res.json()
        else:
            logging.debug(avatar_content_res.text)
            if avatar_content_res.status_code == requests.codes.too_many:
                raise ValueError(
                    (
                        "Response status code is 429! "
                        "You hit Twitter's ratelimit, retry later."
                    )
                )
            if 400 <= avatar_content_res.status_code < 500:
                raise ValueError(
                    "Response code is in the 4XX range. Bad request on our side"
                )
            if avatar_content_res.status_code >= 500:
                raise ValueError(
                    "Response code is over 500. There was an error on Twitter's side"
                )
            raise ValueError("Can't get proper response")

        try:
            broadcast_id = avatar_content["users"][user_id]["spaces"]["live_content"][
                "audiospace"
            ]["broadcast_id"]
        except KeyError as err:
            raise ValueError(
                "Broadcast ID is not available.\nUser is probably not live"
            ) from err
        return cls(cls._metadata(broadcast_id))

    @classmethod
    def from_file(cls, path: str):
        """Create a Twspace instance from a metadata file"""
        with open(path, "r", encoding="utf-8") as metadata_io:
            return cls(json.load(metadata_io))
