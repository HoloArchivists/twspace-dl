import re

import requests


def guest_token() -> str:
    """Generate a guest token to authorize twitter api requests"""
    headers = {
        "authorization": (
            "Bearer "
            "AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs"
            "=1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA"
        )
    }
    response = requests.post(
        "https://api.twitter.com/1.1/guest/activate.json", headers=headers
    ).json()
    token = response.get("guest_token")
    if not isinstance(token, str):
        raise RuntimeError("No guest token found after five retry")
    return token


def user_id(user_url: str) -> str:
    """Get the id of a twitter using the url linking to their account"""
    screen_name = re.findall(r"(?<=twitter.com/)\w*", user_url)[0]
    params = {"screen_names": screen_name}
    response = requests.get(
        "https://cdn.syndication.twimg.com/widgets/followbutton/info.json",
        params=params,
    )
    user_data = response.json()
    if (
        not isinstance(user_data, list)
        or len(user_data) == 0
        or "id" not in user_data[0]
    ):
        raise RuntimeError("No user id found in response")
    user_id = user_data[0]["id"]
    return str(user_id)
