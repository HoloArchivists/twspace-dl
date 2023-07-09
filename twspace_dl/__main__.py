"""Script designed to help download twitter spaces"""
import argparse
import datetime
import json
import logging
import sys
from types import TracebackType
from typing import Optional, Type

from twspace_dl.api import API
from twspace_dl.cookies import load_cookies
from twspace_dl.twspace import Twspace
from twspace_dl.twspace_dl import TwspaceDL

EXIT_CODE_SUCCESS = 0
EXIT_CODE_ERROR = 1
EXIT_CODE_MISUSE = 2


def exception_hook(
    _: Type[BaseException],
    exc_value: BaseException,
    _t: TracebackType = None,
) -> None:
    """Make Exceptions more legible for the end users"""
    # Exception type and value
    print(f"\033[31;1;4mError\033[0m: {exc_value}\nRetry with -v to see more details")


def space(args: argparse.Namespace) -> int:
    """Manage the twitter space related function"""
    has_input = (
        args.user_url
        or args.input_url
        or args.input_metadata
        or args.from_dynamic_url
        or args.from_master_url
    )
    if not has_input:
        print(
            "Either user url, space url, dynamic url or master url should be provided"
        )
        return EXIT_CODE_MISUSE

    if args.log:
        log_filename = datetime.datetime.now().strftime(
            ".twspace-dl.%Y-%m-%d_%H-%M-%S_%f.log"
        )
        handlers: Optional[list[logging.Handler]] = [
            logging.FileHandler(log_filename),
            logging.StreamHandler(),
        ]
    else:
        handlers = None

    if not args.verbose:
        sys.excepthook = exception_hook
        logging.basicConfig(
            level=logging.INFO,
            format="%(levelname)s: %(message)s",
            handlers=handlers,
        )
    else:
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s [%(levelname)s] %(message)s",
            handlers=handlers,
        )

    API.init_apis(load_cookies(args.input_cookie_file))
    if args.user_url:
        twspace = Twspace.from_user_avatar(args.user_url)
    elif args.input_metadata:
        twspace = Twspace.from_file(args.input_metadata)
    elif args.input_url:
        twspace = Twspace.from_space_url(args.input_url)
    else:
        logging.warning(
            (
                "No metadata provided.\n"
                "The resulting file won't be associated with the original space.\n"
                "Please consider adding a space url or a metadata file"
            )
        )
        twspace = Twspace({})
    twspace_dl = TwspaceDL(twspace, args.output)

    if args.from_dynamic_url:
        twspace_dl.dyn_url = args.from_dynamic_url
    if args.from_master_url:
        twspace_dl.master_url = args.from_master_url

    if args.write_metadata:
        with open(f"{twspace_dl.filename}.json", "w", encoding="utf-8") as metadata_io:
            json.dump(twspace.source, metadata_io, indent=4)
    if args.url:
        print(twspace_dl.master_url)
    if args.write_url:
        with open(args.write_url, "a", encoding="utf-8") as url_output:
            url_output.write(f"{twspace_dl.master_url}\n")
    if args.write_playlist:
        twspace_dl.write_playlist()

    if not args.skip_download:
        try:
            twspace_dl.download()
            if args.embed_cover:
                twspace_dl.embed_cover()
        except KeyboardInterrupt:
            logging.info("Download Interrupted by user")
        finally:
            if not args.keep_files:
                twspace_dl.cleanup()
    return EXIT_CODE_SUCCESS


def main() -> int:
    """Main function, creates the argument parser"""
    parser = argparse.ArgumentParser(
        description="Script designed to help download twitter spaces"
    )

    input_group = parser.add_argument_group("input")
    input_method = input_group.add_mutually_exclusive_group()
    output_group = parser.add_argument_group("output")

    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("-s", "--skip-download", action="store_true")
    parser.add_argument("-k", "--keep-files", action="store_true")
    parser.add_argument("-l", "--log", action="store_true", help="create logfile")
    parser.add_argument(
        "-c",
        "--input-cookie-file",
        type=str,
        metavar="COOKIE_FILE",
        help=(
            "cookies file in the Netscape format. The specs of the Netscape cookies format "
            "can be found here: https://curl.se/docs/http-cookies.html. The cookies file is "
            "now required due to the Twitter API change that prohibited guest user access to "
            "Twitter API endpoints on 2023-07-01."
        ),
        required=True,
    )

    input_method.add_argument("-i", "--input-url", type=str, metavar="SPACE_URL")
    input_method.add_argument("-U", "--user-url", type=str, metavar="USER_URL")
    input_group.add_argument(
        "-d",
        "--from-dynamic-url",
        type=str,
        metavar="DYN_URL",
        help=(
            "use the dynamic url for the processes(useful for ended spaces)\n"
            "example: https://prod-fastly-ap-northeast-1.video.pscp.tv/Transcoding/v1/"
            "hls/zUUpEgiM0M18jCGxo2eSZs99p49hfyFQr1l4cdze-Sp4T-DQOMMoZpkbdyetgfwscfvvUk"
            "AdeF-I5hPI4bGoYg/non_transcode/ap-northeast-1/"
            "periscope-replay-direct-prod-ap-northeast-1-public/"
            "audio-space/dynamic_playlist.m3u8?type=live"
        ),
    )
    input_group.add_argument(
        "-f",
        "--from-master-url",
        type=str,
        metavar="URL",
        help=(
            "use the master url for the processes(useful for ended spaces)\n"
            "example: https://prod-fastly-ap-northeast-1.video.pscp.tv/Transcoding/v1/"
            "hls/YRSsw6_P5xUZHMualK5-ihvePR6o4QmoZVOBGicKvmkL_KB9IQYtxVqm3P_"
            "vpZ2HnFkoRfar4_uJOjqC8OCo5A/non_transcode/ap-northeast-1/"
            "periscope-replay-direct-prod-ap-northeast-1-public/"
            "audio-space/master_playlist.m3u8"
        ),
    )
    input_group.add_argument(
        "-M",
        "--input-metadata",
        type=str,
        metavar="PATH",
        help=(
            "use a metadata json file instead of input url\n"
            "(useful for very old ended spaces)"
        ),
    )

    output_group.add_argument(
        "-o",
        "--output",
        type=str,
        metavar="FORMAT_STR",
    )
    output_group.add_argument(
        "-m",
        "--write-metadata",
        action="store_true",
        help="write the full metadata json to a file",
    )
    output_group.add_argument(
        "-p",
        "--write-playlist",
        action="store_true",
        help=(
            "write the m3u8 used to download the stream"
            "(e.g. if you want to use another downloader)"
        ),
    )
    output_group.add_argument(
        "-u", "--url", action="store_true", help="display the master url"
    )
    output_group.add_argument(
        "--write-url", type=str, metavar="URL_OUTPUT", help="write master url to file"
    )
    output_group.add_argument(
        "-e",
        "--embed-cover",
        action="store_true",
        help="embed user avatar as cover art",
    )
    parser.set_defaults(func=space)
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        return EXIT_CODE_ERROR
    args = parser.parse_args()
    args.func(args)
    return EXIT_CODE_SUCCESS


if __name__ == "__main__":
    main()
