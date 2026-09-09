"""Group all followed artists by Spotify genre; no EDM filter is implied."""

import argparse
import json
from pathlib import Path

from spotify_common import create_client, followed_artists, unique_names


def group_by_genre(artists):
    genres = {}
    for artist in artists:
        for genre in artist.get("genres", []):
            genres.setdefault(genre, []).append(artist["name"])
    return {genre: sorted(unique_names(names), key=str.casefold)
            for genre, names in sorted(genres.items())}


def genre_report(genres):
    return "\n".join(
        f"{genre}: {len(names)}\n" + "".join(f"  - {name}\n" for name in names)
        for genre, names in genres.items()
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path("."))
    args = parser.parse_args()
    genres = group_by_genre(followed_artists(create_client("user-follow-read")))
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "different_genres.json").write_text(
        json.dumps(genres, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    report = genre_report(genres)
    for name in ("genres.txt", "genres-refined.txt"):
        (args.output_dir / name).write_text(report, encoding="utf-8")
    print(f"Saved {len(genres)} genres to {args.output_dir}")


if __name__ == "__main__":
    main()
