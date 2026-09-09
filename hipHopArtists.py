"""Export followed artists matching a name prefix (legacy filename retained)."""

import argparse
from pathlib import Path

from spotify_common import create_client, followed_artists


def get_all_and_filter_followed_artists(client, start_character):
    prefix = start_character.strip().casefold()
    if not prefix:
        raise ValueError("The name prefix must not be empty.")
    return sorted({artist["name"] for artist in followed_artists(client)
                   if artist["name"].casefold().startswith(prefix)}, key=str.casefold)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("prefix", help="Name prefix, e.g. A or Lil")
    parser.add_argument("--output", type=Path, default=Path("followed_artists.txt"))
    args = parser.parse_args()
    if not args.prefix.strip():
        parser.error("prefix must not be empty")
    artists = get_all_and_filter_followed_artists(create_client("user-follow-read"), args.prefix)
    args.output.write_text("".join(name + "\n" for name in artists), encoding="utf-8")
    print(f"Saved {len(artists)} artists to {args.output}")


if __name__ == "__main__":
    main()
