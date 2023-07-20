"""Provide an interface with twitter spaces"""
import json
import logging
import os
import re
from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

import requests

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
            if creator_info := root["creator_results"]["result"].get("legacy"):  # type: ignore
                self["creator_name"] = creator_info["name"]  # type: ignore
                self["creator_screen_name"] = creator_info["screen_name"]  # type: ignore
                self["creator_id"] = twitter.user_id(
                    "https://twitter.com/" + creator_info["screen_name"]
                )

            self.source = metadata
            self.root = root
            self["id"] = root["rest_id"]
            self["url"] = "https://twitter.com/i/spaces/" + self["id"]
            self["title"] = root["title"]
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

    @staticmethod
    def _metadata(space_id: str, cookie_str: Optional[str] = None, csrf_token: Optional[str] = None) -> dict:
        params = {
            "variables": (
                "{"
                f'"id":"{space_id}",'
                '"isMetatagsQuery":true,'
                '"withReplays":true,'
                '"withListeners":true'
                "}"
            ),
            "features": (
                "{"
                '"spaces_2022_h2_clipping": true,'
                '"spaces_2022_h2_spaces_communities": true,'
                '"responsive_web_graphql_exclude_directive_enabled": true,'
                '"verified_phone_label_enabled": false,'
                '"creator_subscriptions_tweet_preview_api_enabled": true,'
                '"responsive_web_graphql_skip_user_profile_image_extensions_enabled": false,'
                '"tweetypie_unmention_optimization_enabled": true,'
                '"responsive_web_edit_tweet_api_enabled": true,'
                '"graphql_is_translatable_rweb_tweet_is_translatable_enabled": true,'
                '"view_counts_everywhere_api_enabled": true,'
                '"longform_notetweets_consumption_enabled": true,'
                '"responsive_web_twitter_article_tweet_consumption_enabled": false,'
                '"tweet_awards_web_tipping_enabled": false,'
                '"freedom_of_speech_not_reach_fetch_enabled": true,'
                '"standardized_nudges_misinfo": true,'
                '"tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled": true,'
                '"responsive_web_graphql_timeline_navigation_enabled": true,'
                '"longform_notetweets_rich_text_read_enabled": true,'
                '"longform_notetweets_inline_media_enabled": true,'
                '"responsive_web_media_download_video_enabled": false,'
                '"responsive_web_enhance_cards_enabled": false'
                "}"
            ),
            "fieldToggles": (
                "{"
                '"withAuxiliaryUserLabels":false,'
                '"withArticleRichContentState":false'
                "}"
            )
        }
        headers = {
            "authorization": (
                "Bearer "
                "AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs"
                "=1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA"
            ),
        }
        if cookie_str:
            headers["cookie"] = cookie_str
        else:
            logging.warning("No cookie string provided, request will likely be rejected")

        if csrf_token:
            headers["x-csrf-token"] = csrf_token
        else:
            logging.warning("No csrf token provided, request will likely be rejected")

        response = requests.get(
            "https://twitter.com/i/api/graphql/j0gdijZvHUVbR2fMtxcgHg/AudioSpaceById",
            params=params,
            headers=headers,
            timeout=30,
        )
        response.raise_for_status()
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
    def from_user_tweets(cls, url: str, cookie_str: Optional[str] = None, csrf_token: Optional[str] = None):
        """Create a Twspace instance from the first space
        found in the 20 last user tweets"""
        user_id = twitter.user_id(url)
        headers = {
            "authorization": (
                "Bearer "
                "AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs"
                "=1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA"
            )
        }
        if cookie_str:
            headers["cookie"] = cookie_str
        else:
            logging.warning("No cookie string provided, request will likely be rejected")

        if csrf_token:
            headers["x-csrf-token"] = csrf_token
        else:
            logging.warning("No csrf token provided, request will likely be rejected")

        params = {
            "variables": (
                "{"
                f'"userId":"{user_id}",'
                '"count":20,'
                '"includePromotedContent":true,'
                '"withQuickPromoteEligibilityTweetFields":true,'
                '"withVoice":true,'
                '"withV2Timeline":true'
                "}"
            ),
            "features": (
                "{"
                '"rweb_lists_timeline_redesign_enabled": true,'
                '"responsive_web_graphql_exclude_directive_enabled": true,'
                '"verified_phone_label_enabled": false,'
                '"creator_subscriptions_tweet_preview_api_enabled": true,'
                '"responsive_web_graphql_timeline_navigation_enabled": true,'
                '"responsive_web_graphql_skip_user_profile_image_extensions_enabled": false,'
                '"tweetypie_unmention_optimization_enabled": true,'
                '"responsive_web_edit_tweet_api_enabled": true,'
                '"graphql_is_translatable_rweb_tweet_is_translatable_enabled": true,'
                '"view_counts_everywhere_api_enabled": true,'
                '"longform_notetweets_consumption_enabled": true,'
                '"responsive_web_twitter_article_tweet_consumption_enabled": false,'
                '"tweet_awards_web_tipping_enabled": false,'
                '"freedom_of_speech_not_reach_fetch_enabled": true,'
                '"standardized_nudges_misinfo": true,'
                '"tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled": true,'
                '"longform_notetweets_rich_text_read_enabled": true,'
                '"longform_notetweets_inline_media_enabled": true,'
                '"responsive_web_media_download_video_enabled": false,'
                '"responsive_web_enhance_cards_enabled": false'
                "}"
            ),
            "fieldToggles": (
                "{"
                '"withAuxiliaryUserLabels":false,'
                '"withArticleRichContentState":false'
                "}"
            )
        }
        response = requests.get(
            "https://twitter.com/i/api/graphql/2GIWTr7XwadIixZDtyXd4A/UserTweets",
            params=params,
            headers=headers,
            timeout=30,
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
    def from_user_avatar(cls, user_url, cookie_str: str, csrf_token: Optional[str] = None):
        """Create a Twspace instance from a twitter user's ongoing space"""
        headers = {
            "authorization": (
                "Bearer "
                "AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs"
                "=1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA"
            ),
            "cookie": cookie_str,
        }
        if csrf_token:
            headers["x-csrf-token"] = csrf_token
        else:
            logging.warning(
                "csrf token not provided, "
                "you may encounter a 403 error if you are not logged in"
            )
        user_id = twitter.user_id(user_url)
        params = {"user_ids": user_id, "only_spaces": "true"}
        avatar_content_res = requests.get(
            "https://twitter.com/i/api/fleets/v1/avatar_content",
            params=params,
            headers=headers,
            timeout=30,
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
