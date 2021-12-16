"""twspace_dl formatting helper submodule"""
import os
import re
from collections import defaultdict
from datetime import datetime


# mostly taken from ytarchive
class FormatInfo(dict):
    """
    Simple class to more easily keep track of what fields are available for
    file name formatting
    """

    DEFAULT_FNAME_FORMAT = "(%(creator_name)s)%(title)s-%(id)s"

    def __init__(self) -> None:
        dict.__init__(
            self,
            {
                "id": "",
                "url": "",
                "title": "",
                "creator_name": "",
                "creator_screen_name": "",
                "start_date": "",
            },
        )

    def set_info(self, metadata: dict) -> None:
        root = defaultdict(str, metadata["data"]["audioSpace"]["metadata"])
        creator_info = root["creator_results"]["result"]["legacy"]  # type: ignore
        self["id"] = root["rest_id"]
        self["url"] = "https://twitter.com/i/spaces/" + self["id"]
        self["title"] = root["title"]
        self["creator_name"] = creator_info["name"]  # type: ignore
        self["creator_screen_name"] = creator_info["screen_name"]  # type: ignore
        self["start_date"] = datetime.fromtimestamp(
            int(root["started_at"]) / 1000
        ).strftime("%Y-%m-%d")

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
        actual_format_str = os.path.basename(format_str)
        abs_dir = os.path.dirname(format_str)
        basename = self.sterilize_fn(actual_format_str % self)
        return os.path.join(abs_dir, basename)
