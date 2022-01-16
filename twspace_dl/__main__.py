"""Script designed to help download twitter spaces"""
import argparse
import json
import logging
import os
import shutil
import sys

from twspace_dl.twspace_dl import TwspaceDL
from twspace_dl.login import Login, load_from_file, write_to_file


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Script designed to help download twitter spaces"
    )
    subparsers = parser.add_subparsers(
        help="(EXPERIMENTAL) Login to your account using username and password",
    )
    login_parser = subparsers.add_parser("login", description="EXPERIMENTAL")
    input_group = parser.add_argument_group("input")
    input_method = input_group.add_mutually_exclusive_group()
    output_group = parser.add_argument_group("output")

    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("-s", "--skip-download", action="store_true")
    parser.add_argument("-k", "--keep-files", action="store_true")
    parser.add_argument("--input-cookie-file", type=str, metavar="COOKIE_FILE")

    login_parser.add_argument(
        "-u", "--username", type=str, metavar="USERNAME", default=None
    )
    login_parser.add_argument(
        "-p", "--password", type=str, metavar="PASSWORD", default=None
    )
    login_parser.add_argument(
        "-o",
        "--output-cookie-file",
        type=str,
        metavar="OUTPUT_COOKIE_FILE",
        default=None,
    )
    login_parser.set_defaults(func=login)

    input_method.add_argument("-i", "--input-url", type=str, metavar="SPACE_URL")
    input_method.add_argument("-U", "--user-url", type=str, metavar="USER_URL")
    input_group.add_argument(
        "-d",
        "--from-dynamic-url",
        type=str,
        metavar="DYN_URL",
        help=(
            "use the dynamic url for the processes(useful for ended spaces)\n"
            "example: https://prod-fastly-ap-northeast-1.video.pscp.tv/Transcoding/v1/hls/"
            "zUUpEgiM0M18jCGxo2eSZs99p49hfyFQr1l4cdze-Sp4T-DQOMMoZpkbdyetgfwscfvvUkAdeF-I5hPI4bGoYg/"
            "non_transcode/ap-northeast-1/periscope-replay-direct-prod-ap-northeast-1-public/"
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
            "example: https://prod-fastly-ap-northeast-1.video.pscp.tv/Transcoding/v1/hls/"
            "YRSsw6_P5xUZHMualK5-ihvePR6o4QmoZVOBGicKvmkL_KB9IQYtxVqm3P_vpZ2HnFkoRfar4_uJOjqC8OCo5A/"
            "non_transcode/ap-northeast-1/periscope-replay-direct-prod-ap-northeast-1-public/"
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
    parser.set_defaults(func=twspace)
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)
    args = parser.parse_args()
    args.func(args)


def login(args: argparse.Namespace) -> None:
    has_partial_login = (
        args.username or args.password or args.output_cookie_file  # has at least one
    ) and not (
        args.username and args.password and args.output_cookie_file  # has both
    )  # has one but not both

    if has_partial_login:
        print("login needs both username, password, and output file")
        sys.exit(2)

    if args.username and args.password and args.output_cookie_file:
        login = Login(args.username, args.password, TwspaceDL.guest_token())
        auth_token = login.login()
        write_to_file(auth_token, args.output_cookie_file)


def twspace(args: argparse.Namespace) -> None:
    has_input = (
        args.input_url
        or args.input_metadata
        or args.user_url
        or args.from_master_url
        or args.from_dynamic_url
    )

    if not has_input:
        print("Either space url, user url or master url should be provided")
        sys.exit(2)

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    if args.user_url:
        if args.input_cookie_file:
            auth_token = load_from_file(args.input_cookie_file)
            twspace_dl = TwspaceDL.from_user_avatar(
                args.user_url, args.output, auth_token
            )
        else:
            twspace_dl = TwspaceDL.from_user_tweets(args.user_url, args.output)
    elif args.input_metadata:
        with open(args.input_metadata, "r", encoding="utf-8") as metadata_io:
            metadata = json.load(metadata_io)
        twspace_dl = TwspaceDL(
            metadata["data"]["audioSpace"]["metadata"]["rest_id"], args.output
        )
        twspace_dl.metadata = metadata
    else:
        twspace_dl = TwspaceDL.from_space_url(args.input_url, args.output)

    if args.from_dynamic_url:
        twspace_dl.dyn_url = args.from_dynamic_url
    if args.from_master_url:
        twspace_dl.master_url = args.from_master_url

    if args.write_metadata:
        metadata = json.dumps(twspace_dl.metadata, indent=4)
        filename = twspace_dl.filename
        with open(f"{filename}.json", "w", encoding="utf-8") as metadata_io:
            metadata_io.write(metadata)
    if args.url:
        print(twspace_dl.master_url)
    if args.write_url:
        with open(args.write_url, "a", encoding="utf-8") as url_output:
            url_output.write(twspace_dl.master_url)
    if args.write_playlist:
        twspace_dl.write_playlist()

    if not args.skip_download:
        try:
            twspace_dl.download()
        except KeyboardInterrupt:
            logging.info("Download Interrupted")
        finally:
            if not args.keep_files and os.path.exists(twspace_dl._tmpdir):
                shutil.rmtree(twspace_dl._tmpdir)


if __name__ == "__main__":
    main()
