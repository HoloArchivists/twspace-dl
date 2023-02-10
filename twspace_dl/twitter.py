import logging
import re
import tempfile
import time
from os.path import getmtime, join

import requests

AUTH_HEADER = {
    "authorization": (
        "Bearer "
        "AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs"
        "=1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA"
    )
}
GUEST_TOKEN = None
GUEST_TOKEN_FILE = join(tempfile.gettempdir(), "twspace_dl-guest_token")
GUEST_TOKEN_TIMEOUT = 1800


def guest_token(refresh: bool = False) -> str:
    """Generate a guest token to authorize twitter api requests"""
    global GUEST_TOKEN
    if not GUEST_TOKEN or refresh:
        try:
            if (
                refresh
                or time.time() - getmtime(GUEST_TOKEN_FILE) > GUEST_TOKEN_TIMEOUT
            ):
                raise FileNotFoundError
            with open(GUEST_TOKEN_FILE) as f:
                GUEST_TOKEN = f.read()
        except FileNotFoundError:
            response = requests.post(
                "https://api.twitter.com/1.1/guest/activate.json",
                headers=AUTH_HEADER,
                timeout=30,
            ).json()
            if GUEST_TOKEN := response["guest_token"]:
                try:
                    with open(GUEST_TOKEN_FILE, "w") as f:
                        f.write(GUEST_TOKEN)
                except OSError as e:
                    logging.error(e)
            else:
                raise RuntimeError("No guest token found after five retry")
    return GUEST_TOKEN


def user_id(user_url: str) -> str:
    """Get the id of a twitter using the url linking to their account"""
    screen_name = re.findall(r"(?<=twitter.com/)\w*", user_url)[0]
    params = {
        "variables": (
            "{"
            f'"screen_name":"{screen_name}",'
            '"withSafetyModeUserFields":false,'
            '"withSuperFollowsUserFields":false'
            "}"
        )
    }
    session = requests.Session()
    req = requests.Request(
        "GET",
        "https://twitter.com/i/api/graphql/7mjxD3-C6BxitPMVQ6w0-Q/UserByScreenName",
        params=params,
        headers={**AUTH_HEADER, "x-guest-token": guest_token()},
    ).prepare()
    response = session.send(req, timeout=30)
    if response.status_code == requests.codes.too_many_requests:
        req.headers.update({"x-guest-token": guest_token(True)})
        response = session.send(req)
    usr_id = response.json()["data"]["user"]["result"]["rest_id"]
    return usr_id
