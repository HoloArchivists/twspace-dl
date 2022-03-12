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
    token = response["guest_token"]
    if not token:
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
    usr_id = user_data[0]["id"]
    return usr_id
