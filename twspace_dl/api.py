from __future__ import annotations

import json
import logging
import re
from typing import Any, NoReturn

import requests
from requests.adapters import HTTPAdapter, Retry
from requests.exceptions import (ConnectionError, HTTPError, JSONDecodeError,
                                 RetryError)

from .cookies import validate_cookies

"""Twitter unofficial API authorization header."""
TWITTER_AUTHORIZATION = "Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs=1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA"

"""Retry parameters for making all requests."""
RETRY = Retry(
    total=5,
    connect=3,
    read=2,
    redirect=3,
    backoff_factor=0.2,
    status_forcelist=(500, 502, 503, 504),
)

"""Default connection timeout for making all requests."""
TIMEOUT = 20


class HTTPClient:
    """The HTTP client for making requests."""

    def __init__(self) -> None:
        """Initialize the client with a requests session and mount the default retry adapter."""
        self.session = requests.Session()
        self.session.mount("https://", HTTPAdapter(max_retries=RETRY))

    def get(
        self,
        url: str,
        params: dict[str, str] = {},
        headers: dict[str, str] = {},
        cookies: dict[str, str] = {},
        timeout: int = TIMEOUT,
    ) -> requests.Response:
        """Send HTTP GET requests to the specified URL.

        - url: The URL to send the GET request to.
        - params: Query parameters of the request.
        - headers: HTTP headers of the request.
        - cookies: HTTP cookies of the request.
        - timeout: The connection timeout of the request, default to the static value specified above.

        - return: The response of the request.

        - raise RuntimeError: Raised when the request was not successful (max retries, timeouts, and
          4xx and 5xx HTTP status codes).
        """
        try:
            response = self.session.get(
                url, params=params, headers=headers, cookies=cookies, timeout=timeout
            )
            response.raise_for_status()
            return response
        except RetryError as e:
            logging.error(
                f"Max retries exceeded with URL: {e.request.url}, reason: {e.args[0].reason}"
            )
            raise RuntimeError("API request failed after max retries") from e
        except ConnectionError as e:
            logging.error(
                f"Connection error occurred with URL: {e.request.url}, reason: {e.args[0].reason}"
            )
            raise RuntimeError("API request failed with connection error") from e
        except HTTPError as e:
            if e.response.status_code == requests.codes.TOO_MANY_REQUESTS:
                logging.error(f"API rate limit exceeded with URL: {url}")
                raise
            logging.error(
                f"HTTP error occurred with URL: {e.request.url}, status code: {e.response.status_code}"
            )
            raise RuntimeError("API request failed with HTTP error") from e


class APIClient:
    """Base API client."""

    """Base URL of the API."""
    _API_URL = "https://twitter.com/i/api"

    def __init__(self, client: HTTPClient, path: str, cookies: dict[str, str]) -> None:
        """Initialize the API client.

        - client: The `HTTPClient` instance to send requests.
        - path: The path to add to the base URL of the API.
        - cookies: The cookies used for making all requests to the API.
        """
        validate_cookies(cookies)
        self.client = client
        self.base_url = self.join_url(self._API_URL, path)
        self.cookies = cookies
        self.headers = {
            "authorization": TWITTER_AUTHORIZATION,
            "x-csrf-token": cookies["ct0"],
        }

    def join_url(self, *paths: str) -> str:
        """Join all the specified paths to a single URL.

        - paths: The components of the URL to be joined.
        """
        return "/".join(path.strip("/") for path in paths)

    def get(self, path: str, params: dict[str, str] = {}) -> Any:
        """Send HTTP GET requests to the specified path of the API with the specified query parameters.

        - path: The path to send the API request to.
        - params: Query parameters of the request.

        - return: The object decoded from the JSON string returned from the API.

        - raise RuntimeError: If the response from the API cannot be decoded as a JSON string.
        """
        try:
            response = self.client.get(
                self.join_url(self.base_url, path),
                params=params,
                headers=self.headers,
                cookies=self.cookies,
            )
            return response.json()
        except JSONDecodeError:
            logging.error(
                f"Cannot decode response from URL: {response.url}, status code: {response.status_code}"
            )
            logging.debug(f"Response text: {response.text!r}")
            raise RuntimeError("API response cannot be decoded as JSON")


class GraphQLAPI(APIClient):
    """Twitter GraphQL API client."""

    def __init__(self, client: HTTPClient, path: str, cookies: dict[str, str]) -> None:
        """Initialize the Twitter GraphQL API client.

        - client: The `HTTPClient` instance to send requests.
        - path: The path to add to the base URL of the API.
        - cookies: The cookies used for making all requests to the API.
        """
        super().__init__(client, path, cookies)

    def _dump_json(self, obj: Any) -> str:
        """Serialize the object to a compact JSON string.

        The object will be returned directly if it is a string.

        - obj: The object to be serialized to JSON.

        - return: A compact JSON string representing the specified object.
        """
        if isinstance(obj, str):
            return obj
        return json.dumps(obj, indent=None, separators=(",", ":"))

    def get(
        self,
        query_id: str,
        operation_name: str,
        variables: dict[str, str] | str,
        features: dict[str, str] | str | None = None,
    ) -> Any:
        """Send HTTP GET requests to the Twitter GraphQL API.

        - query_id: The query ID of the GraphQL API endpoint.
        - operation_name: The name of the operation to be executed.
        - variables: Query variables of the GraphQL query.
        - features: Feature switches of the GraphQL query.

        - return: The returned object of the query.
        """
        params = {"variables": self._dump_json(variables)}
        if features:
            params["features"] = self._dump_json(features)
        return super().get(self.join_url(query_id, operation_name), params)

    def audio_space_by_id(self, space_id: str) -> dict:
        """Query Twitter Space details by its ID.

        - space_id: The ID of the Twitter Space.

        - return: The details of the queried Twitter Space.
        """
        query_id = "xVEzTKg_mLTHubK5ayL0HA"
        operation_name = "AudioSpaceById"
        variables = {
            "id": space_id,
            "isMetatagsQuery": True,
            "withReplays": True,
            "withListeners": True,
        }
        # "features" is copied as-is from real requests
        features = '{"spaces_2022_h2_clipping":true,"spaces_2022_h2_spaces_communities":true,"responsive_web_graphql_exclude_directive_enabled":true,"verified_phone_label_enabled":false,"creator_subscriptions_tweet_preview_api_enabled":true,"responsive_web_graphql_skip_user_profile_image_extensions_enabled":false,"tweetypie_unmention_optimization_enabled":true,"responsive_web_edit_tweet_api_enabled":true,"graphql_is_translatable_rweb_tweet_is_translatable_enabled":true,"view_counts_everywhere_api_enabled":true,"longform_notetweets_consumption_enabled":true,"responsive_web_twitter_article_tweet_consumption_enabled":false,"tweet_awards_web_tipping_enabled":false,"freedom_of_speech_not_reach_fetch_enabled":true,"standardized_nudges_misinfo":true,"tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled":true,"responsive_web_graphql_timeline_navigation_enabled":true,"longform_notetweets_rich_text_read_enabled":true,"longform_notetweets_inline_media_enabled":true,"responsive_web_media_download_video_enabled":false,"responsive_web_enhance_cards_enabled":false}'
        return self.get(query_id, operation_name, variables, features)

    def user_by_screen_name(self, screen_name: str) -> dict:
        """Query Twitter user details by their screen name (@ handle).

        - screen_name: The screen name (@ handle) of the Twitter user.

        - return: The details of the queried Twitter user.
        """
        query_id = "oUZZZ8Oddwxs8Cd3iW3UEA"
        operation_name = "UserByScreenName"
        variables = {"screen_name": screen_name, "withSafetyModeUserFields": True}
        # "features" is copied as-is from real requests
        features = '{"hidden_profile_likes_enabled":false,"responsive_web_graphql_exclude_directive_enabled":true,"verified_phone_label_enabled":false,"subscriptions_verification_info_verified_since_enabled":true,"highlights_tweets_tab_ui_enabled":true,"creator_subscriptions_tweet_preview_api_enabled":true,"responsive_web_graphql_skip_user_profile_image_extensions_enabled":false,"responsive_web_graphql_timeline_navigation_enabled":true}'
        return self.get(query_id, operation_name, variables, features)

    def profile_spotlights_query(self, screen_name: str) -> dict:
        """Backup API endpoint to query Twitter user details by their screen name (@ handle).

        The response data from this API contains less information of the user than the `user_by_screen_name`
        API, but still has the essential `rest_id` field. Therefore, it is used as a backup of the other API
        endpoint if the other one was rate limited.

        - screen_name: The screen name (@ handle) of the Twitter user.

        - return: The details of the queried Twitter user.
        """
        query_id = "ZQEuHPrIYlvh1NAyIQHP_w"
        operation_name = "ProfileSpotlightsQuery"
        variables = {"screen_name": screen_name}
        return self.get(query_id, operation_name, variables)

    def user_id(self, screen_name: str) -> str:
        """Retrieve the numeric user ID (`rest_id`) of the user with the specified screen name (@ handle).

        - screen_name: The screen name (@ handle) of the Twitter user.

        - return: The numeric user ID (`rest_id`) of the specified user.
        """
        try:
            data = self.user_by_screen_name(screen_name)
            return data["data"]["user"]["result"]["rest_id"]
        except HTTPError:
            logging.warning("Trying with backup endpoint")
            data = self.profile_spotlights_query(screen_name)
            return data["data"]["user_result_by_screen_name"]["result"]["rest_id"]

    def user_id_from_url(self, user_url: str) -> str:
        """Retrieve the numeric user ID (`rest_id`) of the user that the specified profile URL linked to.

        Supported URL formats:
        - https://twitter.com/<screen_name>
        - http://twitter.com/<screen_name>
        - twitter.com/<screen_name>
        and with any number of trailing slashes (`/`).

        - user_url: The URL pointing to the profile of the Twitter user.

        - return: The numeric user ID (`rest_id`) of the specified user.

        - raise RuntimeError: If the specified URL is not a valid Twitter user profile URL.
        """
        if match := re.match(
            r"^(?:https?:\/\/|)twitter\.com\/(?P<screen_name>\w+)$", user_url.strip("/")
        ):
            return self.user_id(match.group("screen_name"))
        raise RuntimeError(f"Invalid Twitter user URL: {user_url}")


class FleetsAPI(APIClient):
    """Twitter Fleets API client."""

    def __init__(self, client: HTTPClient, path: str, cookies: dict[str, str]) -> None:
        """Initialize the Twitter Fleets API client.

        - client: The `HTTPClient` instance to send requests.
        - path: The path to add to the base URL of the API.
        - cookies: The cookies used for making all requests to the API.
        """
        super().__init__(client, path, cookies)

    def get(self, version: str, endpoint: str, params: dict[str, str]) -> Any:
        """Send HTTP GET requests to the Twitter Fleets API.

        - version: The version of the API.
        - endpoint: The endpoint of the API.
        - params: Query parameters of the request.

        - return: The object returned in the response of the API.
        """
        return super().get(self.join_url(version, endpoint), params)

    def avatar_content(self, *user_ids: str) -> dict:
        """Retrieve Twitter Space details of the specified user IDs.

        This endpoint limits to a maximum of 100 user IDs per request.

        - user_ids: Numeric user IDs (`rest_id`) of users.

        - return: Twitter Space details of the specified user IDs. Only ongoing Twitter Spaces will be returned.
        """
        if len(user_ids) > 100:
            raise RuntimeError(
                "Number of user IDs exceeded the limit of 100 per request"
            )
        version = "v1"
        endpoint = "avatar_content"
        params = {"user_ids": ",".join(user_ids), "only_spaces": "true"}
        return self.get(version, endpoint, params)


class LiveVideoStreamAPI(APIClient):
    """Twitter Live Video Stream API client."""

    def __init__(self, client: HTTPClient, path: str, cookies: dict[str, str]) -> None:
        """Initialize the Twitter Live Video Stream API client.

        - client: The `HTTPClient` instance to send requests.
        - path: The path to add to the base URL of the API.
        - cookies: The cookies used for making all requests to the API.
        """
        super().__init__(client, path, cookies)

    def status(self, media_key: str) -> dict:
        """Retrieve Twitter Space media playlist details by the specified media key.

        - media_key: The media key of the Twitter Space.

        - return: The media playlist details of the specified media key.
        """
        return super().get(self.join_url("status", media_key))


class DummyAPI:
    """Dummy API class used for uninitialized APIs."""

    def __init__(self, api_name: str = "API") -> None:
        self.api_name = api_name

    def __getattr__(self, name: str) -> NoReturn:
        """Show a clear message to the user if the API was not initialized.

        - raise RuntimeError: If any attribute of the class is accessed or any method is called.
        """
        raise RuntimeError(f"{self.api_name} is not initialized")

    def __bool__(self) -> False:
        """Always evaluate instances of the class to `False`.

        This is just for the convenience of testing the instance directly in `if` statements:
        >>> api = DummyAPI()
        ... if api:  # non-dummy API instances would evaluate to `True`
        ...     # do something if the API was initialized
        ...     pass
        See also: `TwitterAPI.__bool__()`

        - return: `False`.
        """
        return False


class TwitterAPI:
    """The collection of all Twitter APIs."""

    def __init__(self) -> None:
        """Initialize the instance of the Twitter API collection.

        Note that this will not initialize APIs in this collection. They will initially only be an
        instance of the `DummyAPI` class.
        They need to be initialized by calling the `init_apis()` method with cookies of the user.
        """
        self.client = HTTPClient()
        self.graphql_api = DummyAPI("Twitter GraphQL API")
        self.fleets_api = DummyAPI("Twitter Fleets API")
        self.live_video_stream_api = DummyAPI("Twitter Live Video Stream API")

    def init_apis(self, cookies: dict[str, str]) -> None:
        """Initialize all APIs in this collection with the specified cookies."""
        self.graphql_api = GraphQLAPI(self.client, "graphql", cookies)
        self.fleets_api = FleetsAPI(self.client, "fleets", cookies)
        self.live_video_stream_api = LiveVideoStreamAPI(
            self.client, "1.1/live_video_stream", cookies
        )

    def __bool__(self) -> bool:
        """Determine if all APIs are initialized.

        This is just for the convenience of testing the instance directly in `if` statements:
        >>> api = TwitterAPI()
        ... if api:
        ...     print("API initialized")  # would run if all APIs in the `api` instance are initialized
        See also: `DummyAPI.__bool__()`

        - return: `True` if and only if all APIs are initialized, `False` otherwise.
        """
        return bool(self.graphql_api and self.fleets_api and self.live_video_stream_api)


"""The global instance of the collection of Twitter APIs."""
API = TwitterAPI()
