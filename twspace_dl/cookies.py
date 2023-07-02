import re

from .api import REQUIRED_COOKIES


class CookiesLoader:
    COOKIES_PATTERN = re.compile(
        r"\s+({keys})\s+(\w+)$".format(keys="|".join(REQUIRED_COOKIES)),
        re.MULTILINE
    )

    def __init__(self) -> None:
        pass

    @classmethod
    def load(cls, path: str) -> dict[str, str]:
        try:
            with open(path, encoding="utf-8") as f:
                return dict(cls.COOKIES_PATTERN.findall(f.read()))
        except OSError as e:
            raise RuntimeError(f"Cannot load cookies from file: {e.filename}") from e
