#!/usr/bin/env python3
"""Fetch and print a transcript for a YouTube video."""

import argparse
import sys

from transcript_service import TranscriptFetcher, TranscriptError


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url", help="YouTube video URL or id")
    parser.add_argument(
        "--languages",
        nargs="*",
        default=None,
        help="Preferred transcript languages, e.g. en en-US",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    fetcher = TranscriptFetcher(preferred_languages=args.languages)

    try:
        transcript = fetcher.fetch(args.url)
    except TranscriptError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(transcript)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
