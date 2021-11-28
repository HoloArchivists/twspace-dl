from collections import defaultdict
from datetime import datetime


# mostly taken from ytarchive
class FormatInfo(dict):
    """
    Simple class to more easily keep track of what fields are available for
    file name formatting
    """

    DEFAULT_FNAME_FORMAT = "[%(creator_name)s]%(title)s-%(id)s"

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
        self["url"] = "https://twitter.com/spaces/" + self["id"]
        self["title"] = root["title"]
        self["creator_name"] = creator_info["name"]  # type: ignore
        self["creator_screen_name"] = creator_info["screen_name"]  # type: ignore
        self["start_date"] = datetime.fromtimestamp(
            int(root["started_at"]) / 1000
        ).strftime("%Y-%m-%d")

    @staticmethod
    def sterilize_fn(filename: str) -> str:
        bad_chars = '<>:"/\\|?*'
        for char in bad_chars:
            filename.replace(char, "_")
        return filename

    def format(self, format_str: str) -> str:
        return format_str % self
