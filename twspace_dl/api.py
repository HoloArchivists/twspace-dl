import json
import logging
import re
from typing import Any, NoReturn

import requests
from requests.adapters import HTTPAdapter, Retry
from requests.exceptions import (
    ConnectionError, HTTPError, JSONDecodeError, RetryError
)

TWITTER_AUTHORIZATION = "Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs=1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA"
REQUIRED_COOKIES = {"auth_token", "ct0"}
RETRY = Retry(
    total=5,
    connect=3,
    read=2,
    redirect=3,
    backoff_factor=0.2,
    status_forcelist=(429, 500, 502, 503, 504)
)
TIMEOUT = 20


class HTTPClient:
    def __init__(self) -> None:
        self.session = requests.Session()
        self.session.mount("https://", HTTPAdapter(max_retries=RETRY))

    def get(
        self,
        url: str,
        params: dict[str, str] = {},
        headers: dict[str, str] = {},
        cookies: dict[str, str] = {},
        timeout: int = TIMEOUT
    ) -> requests.Response:
        try:
            response = self.session.get(
                url,
                params=params,
                headers=headers,
                cookies=cookies,
                timeout=timeout
            )
            response.raise_for_status()
            return response
        except RetryError as e:
            logging.error(f"Max retries exceeded with URL: {e.request.url}, reason: {e.args[0].reason}")
            raise RuntimeError("API request failed after max retries")
        except ConnectionError as e:
            logging.error(f"Connection error occurred with URL: {e.request.url}, reason: {e.args[0].reason}")
            raise RuntimeError("API request failed with connection error")
        except HTTPError as e:
            logging.error(f"HTTP error occurred with URL: {e.request.url}, status code: {e.response.status_code}")
            raise RuntimeError("API request failed with HTTP error")


class APIClient:
    _API_URL = "https://twitter.com/i/api"

    def __init__(self, client: HTTPClient, path: str, cookies: dict[str, str]) -> None:
        if missing := REQUIRED_COOKIES - cookies.keys():
            raise RuntimeError(f"Missing required cookies: {', '.join(missing)}")
        self.client = client
        self.base_url = self.join_url(self._API_URL, path)
        self.cookies = cookies
        self.headers = {
            "authorization": TWITTER_AUTHORIZATION,
            "x-csrf-token": cookies["ct0"]
        }

    def join_url(self, *paths: str) -> str:
        return "/".join(path.strip("/") for path in paths)

    def get(self, path: str, params: dict[str, str] = {}) -> Any:
        try:
            response = self.client.get(
                self.join_url(self.base_url, path),
                params=params,
                headers=self.headers,
                cookies=self.cookies
            )
            return response.json()
        except JSONDecodeError:
            logging.error(f"Cannot decode response from URL: {response.url}, status code: {response.status_code}")
            logging.debug(f"Response text: {response.text!r}")
            raise RuntimeError("API response cannot be decoded as JSON")


class GraphQLAPI(APIClient):
    def __init__(self, client: HTTPClient, path: str, cookies: dict[str, str]) -> None:
        super().__init__(client, path, cookies)

    def _dump_json(self, obj: Any) -> str:
        if isinstance(obj, str):
            return obj
        return json.dumps(obj, indent=None, separators=(",", ":"))

    def get(
        self,
        query_id: str,
        operation_name: str,
        variables: dict[str, str] | str,
        features: dict[str, str] | str
    ) -> Any:
        return super().get(
            self.join_url(query_id, operation_name),
            {
                "variables": self._dump_json(variables),
                "features": self._dump_json(features)
            }
        )

    def audio_space_by_id(self, space_id: str) -> dict:
        query_id = "xVEzTKg_mLTHubK5ayL0HA"
        operation_name = "AudioSpaceById"
        variables = {
            "id": space_id,
            "isMetatagsQuery": True,
            "withReplays": True,
            "withListeners": True
        }
        features = '{"spaces_2022_h2_clipping":true,"spaces_2022_h2_spaces_communities":true,"responsive_web_graphql_exclude_directive_enabled":true,"verified_phone_label_enabled":false,"creator_subscriptions_tweet_preview_api_enabled":true,"responsive_web_graphql_skip_user_profile_image_extensions_enabled":false,"tweetypie_unmention_optimization_enabled":true,"responsive_web_edit_tweet_api_enabled":true,"graphql_is_translatable_rweb_tweet_is_translatable_enabled":true,"view_counts_everywhere_api_enabled":true,"longform_notetweets_consumption_enabled":true,"responsive_web_twitter_article_tweet_consumption_enabled":false,"tweet_awards_web_tipping_enabled":false,"freedom_of_speech_not_reach_fetch_enabled":true,"standardized_nudges_misinfo":true,"tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled":true,"responsive_web_graphql_timeline_navigation_enabled":true,"longform_notetweets_rich_text_read_enabled":true,"longform_notetweets_inline_media_enabled":true,"responsive_web_media_download_video_enabled":false,"responsive_web_enhance_cards_enabled":false}'
        return self.get(query_id, operation_name, variables, features)

    def user_by_screen_name(self, screen_name: str) -> dict:
        query_id = "oUZZZ8Oddwxs8Cd3iW3UEA"
        operation_name = "UserByScreenName"
        variables = {
            "screen_name": screen_name,
            "withSafetyModeUserFields": True
        }
        features = '{"hidden_profile_likes_enabled":false,"responsive_web_graphql_exclude_directive_enabled":true,"verified_phone_label_enabled":false,"subscriptions_verification_info_verified_since_enabled":true,"highlights_tweets_tab_ui_enabled":true,"creator_subscriptions_tweet_preview_api_enabled":true,"responsive_web_graphql_skip_user_profile_image_extensions_enabled":false,"responsive_web_graphql_timeline_navigation_enabled":true}'
        return self.get(query_id, operation_name, variables, features)

    def user_id(self, screen_name: str) -> str:
        data = self.user_by_screen_name(screen_name)
        return data["data"]["user"]["result"]["rest_id"]

    def user_id_from_url(self, user_url: str) -> str:
        if match := re.match(r"^(?:https?:\/\/|)twitter\.com\/(?P<screen_name>\w+)$", user_url.strip("/")):
            return self.user_id(match.group("screen_name"))
        raise RuntimeError(f"Invalid Twitter user URL: {user_url}")


class FleetsAPI(APIClient):
    def __init__(self, client: HTTPClient, path: str, cookies: dict[str, str]) -> None:
        super().__init__(client, path, cookies)

    def get(self, version: str, endpoint: str, params: dict[str, str]) -> Any:
        return super().get(self.join_url(version, endpoint), params)

    def avatar_content(self, *user_ids: str) -> dict:
        if len(user_ids) > 100:
            raise RuntimeError("Number of user IDs exceeded the limit of 100 per request")
        version = "v1"
        endpoint = "avatar_content"
        params = {
            "user_ids": ",".join(user_ids),
            "only_spaces": "true"
        }
        return self.get(version, endpoint, params)


class LiveVideoStreamAPI(APIClient):
    def __init__(self, client: HTTPClient, path: str, cookies: dict[str, str]) -> None:
        super().__init__(client, path, cookies)

    def status(self, media_key: str) -> dict:
        return super().get(self.join_url("status", media_key))


class DummyAPI:
    def __init__(self) -> None:
        pass

    def __getattr__(self, name: str) -> NoReturn:
        raise RuntimeError("APIs are not initialized")

    def __bool__(self) -> False:
        return False


class TwitterAPI:
    def __init__(self) -> None:
        self.client = HTTPClient()
        self.graphql_api = self.fleets_api = self.live_video_stream_api = DummyAPI()

    def init_apis(self, cookies: dict[str, str]) -> None:
        self.graphql_api = GraphQLAPI(self.client, "graphql", cookies)
        self.fleets_api = FleetsAPI(self.client, "fleets", cookies)
        self.live_video_stream_api = LiveVideoStreamAPI(self.client, "1.1/live_video_stream", cookies)

    def __bool__(self) -> bool:
        return bool(self.graphql_api and self.fleets_api and self.live_video_stream_api)


API = TwitterAPI()
