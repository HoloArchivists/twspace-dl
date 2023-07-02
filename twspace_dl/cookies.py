import re

from .api import REQUIRED_COOKIES


class CookiesLoader:
    """Loader of cookies files.

    Compatible with cookies file in Netscape format.
    More details of the format: https://curl.se/docs/http-cookies.html
    """

    """The regex pattern to extract keys and values of all required cookies."""
    COOKIES_PATTERN = re.compile(
        r"\s+({keys})\s+(\w+)$".format(keys="|".join(REQUIRED_COOKIES)),
        re.MULTILINE
    )

    def __init__(self) -> None:
        pass

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
