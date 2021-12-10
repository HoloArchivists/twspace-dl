"""Script designed to help download twitter spaces"""
import argparse
import logging
import os
import shutil
import sys

from .TwspaceDL import TwspaceDL


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Script designed to help download twitter spaces"
    )
    input_group = parser.add_argument_group("input")
    output_group = parser.add_argument_group("output")

    parser.add_argument(
        "-t",
        "--threads",
        type=int,
        metavar="THREADS",
        help="number of threads to run the script with(default with max)",
        default=os.cpu_count(),
    )
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("-s", "--skip-download", action="store_true")
    parser.add_argument("-k", "--keep-files", action="store_true")

    input_group.add_argument("-i", "--input-url", type=str, metavar="SPACE_URL")
    input_group.add_argument("-U", "--user-url", type=str, metavar="USER_URL")
    input_group.add_argument(
        "-d",
        "--from-dynamic-url",
        type=str,
        metavar="DYN_URL",
        help="use the master url for the processes(useful for ended spaces)",
    )

    input_group.add_argument(
        "-f",
        "--from-master-url",
        type=str,
        metavar="URL",
        help="use the master url for the processes(useful for ended spaces)",
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

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)
    args = parser.parse_args()
    return args


def main() -> None:
    args = get_args()
    if not args.input_url and not args.user_url and not args.from_master_url:
        print("Either space url, user url or master url should be provided")
        sys.exit(1)

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    if args.input_url:
        twspace_dl = TwspaceDL.from_space_url(args.input_url, args.threads, args.output)
    else:
        twspace_dl = TwspaceDL.from_user_url(args.user_url, args.threads, args.output)
    if args.from_dynamic_url:
        twspace_dl.dyn_url = args.from_dynamic_url
    if args.from_master_url:
        twspace_dl.master_url = args.from_master_url
    if args.write_metadata:
        twspace_dl.write_metadata()
    if args.url:
        print(twspace_dl.master_url)
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
