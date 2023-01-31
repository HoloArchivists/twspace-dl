import re

import requests

AUTH_HEADER = {
    "authorization": (
        "Bearer "
        "AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs"
        "=1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA"
    )
}


def guest_token() -> str:
    """Generate a guest token to authorize twitter api requests"""
    response = requests.post(
        "https://api.twitter.com/1.1/guest/activate.json",
        headers=AUTH_HEADER,
        timeout=30,
    ).json()
    token = response["guest_token"]
    if not token:
        raise RuntimeError("No guest token found after five retry")
    return token


def user_id(user_url: str) -> str:
    """Get the id of a twitter using the url linking to their account"""
    screen_name = re.findall(r"(?<=twitter.com/)\w*", user_url)[0]
    params = {
        "variables": (
            "{"
            f'"screen_name":"{screen_name}",'
            '"withSafetyModeUserFields":true,'
            '"withSuperFollowsUserFields":true'
            "}"
        ),
        "features": (
            "{"
            '"responsive_web_twitter_blue_verified_badge_is_enabled":true,'
            '"verified_phone_label_enabled":false,'
            '"responsive_web_graphql_timeline_navigation_enabled":true'
            "}"
        ),
    }
    response = requests.get(
        "https://api.twitter.com/graphql/hVhfo_TquFTmgL7gYwf91Q/UserByScreenName",
        params=params,
        headers=AUTH_HEADER | {"x-guest-token": guest_token()},
        timeout=30,
    ).json()
    usr_id = response["data"]["user"]["result"]["rest_id"]
    return usr_id
