import re


class CookiesLoader:
    """Loader of cookies files.

    Compatible with cookies file in Netscape format.
    More details of the format: https://curl.se/docs/http-cookies.html
    """

    """The template to match hex strings of the specified length."""
    HEX_TEMPLATE = "(?:[0-9a-f]{{2}}){{{length}}}"

    """Regex patterns to validate values of the specified cookies."""
    VALID_COOKIES = {
        "auth_token": re.compile(HEX_TEMPLATE.format(length=20)),
        "ct0": re.compile(HEX_TEMPLATE.format(length=80))
    }

    """The regex pattern to extract keys and values of all required cookies."""
    COOKIES_PATTERN = re.compile(
        r"\s+({keys})\s+({values})$".format(
            keys="|".join(VALID_COOKIES.keys()),
            values=HEX_TEMPLATE.format(length="20,80")
        ),
        re.MULTILINE
    )

    @classmethod
    def load(cls, path: str) -> dict[str, str]:
        """Load cookies from the specified path.

        - path: The path to the cookies file.

        - return: A `dict` of keys and values of all required cookies.

        - raise RuntimeError: If the cookies file failed to load.
        """
        try:
            with open(path, encoding="utf-8") as f:
                return dict(cls.COOKIES_PATTERN.findall(f.read()))
        except OSError as e:
            raise RuntimeError(f"Cannot load cookies from file: {e.filename}") from e

    @classmethod
    def validate(cls, cookies: dict[str, str]) -> None:
        """Validate the specified cookies.

        - cookies: The cookies to be validated.

        - raise TypeError: If there were missing or extra cookies.
        - raise ValueError: If there were invalid cookies values.
        """
        if missing := cls.VALID_COOKIES.keys() - cookies.keys():
            raise TypeError(f"Missing required cookies: {', '.join(missing)}")
        if extra := cookies.keys() - cls.VALID_COOKIES.keys():
            raise TypeError(f"Extra cookies: {', '.join(extra)}")
        if invalid := {key for key, value in cookies.items() if not cls.VALID_COOKIES[key].fullmatch(str(value))}:
            raise ValueError(f"Invalid cookies: {', '.join(invalid)}")
