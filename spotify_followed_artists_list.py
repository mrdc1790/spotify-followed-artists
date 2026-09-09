"""Export followed artists in Spotify's returned order, without follow-date claims."""

import argparse
from datetime import datetime
from pathlib import Path

from spotify_common import create_client, followed_artists


def export_artists(artists, output):
    with Path(output).open("w", encoding="utf-8") as handle:
        handle.write(f"Total artists: {len(artists)}\n\n")
        for index, artist in enumerate(artists, 1):
            followers = (artist.get("followers") or {}).get("total")
            popularity = artist.get("popularity")
            handle.write(f"{index}. {artist['name']}\n")
            handle.write(f"   Followers: {followers:,}\n" if followers is not None
                         else "   Followers: N/A\n")
            handle.write(f"   Popularity: {popularity if popularity is not None else 'N/A'}\n")
            handle.write(f"   Genres: {', '.join(artist.get('genres', []))}\n")
            handle.write(f"   URL: {artist['external_urls']['spotify']}\n\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--reverse", action="store_true", help="Reverse API order, not chronological order")
    args = parser.parse_args()
    artists = list(followed_artists(create_client("user-follow-read")))
    if args.reverse:
        artists.reverse()
    output = args.output or Path(f"spotify_followed_artists_{datetime.now():%Y%m%d_%H%M%S}.txt")
    export_artists(artists, output)
    print(f"Saved {len(artists)} artists to {output}")


if __name__ == "__main__":
    main()
