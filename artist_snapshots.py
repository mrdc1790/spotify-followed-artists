"""Export and compare followed-artist snapshots by Spotify artist ID."""

import argparse
import csv
from datetime import datetime, timezone
import json
from pathlib import Path


SCHEMA_VERSION = 1
ARTIST_FIELDS = ("spotify_id", "name", "spotify_url", "genres", "followers", "popularity")


def index_artists(artists):
    if not isinstance(artists, list):
        raise ValueError("Expected an artists list.")
    indexed = {}
    for artist in artists:
        if not isinstance(artist, dict):
            raise ValueError("Expected each artist to be an object.")
        spotify_id = artist.get("spotify_id")
        name = artist.get("name")
        genres = artist.get("genres")
        if not isinstance(spotify_id, str) or not spotify_id.strip():
            raise ValueError("Each artist needs a Spotify ID.")
        if spotify_id in indexed:
            raise ValueError(f"Duplicate Spotify artist ID: {spotify_id}")
        if not isinstance(name, str) or not name.strip():
            raise ValueError(f"Missing artist name for {spotify_id}.")
        if genres is not None and (
            not isinstance(genres, list) or any(not isinstance(genre, str) for genre in genres)
        ):
            raise ValueError(f"Expected a genre list or null for {spotify_id}.")
        indexed[spotify_id] = artist
    return indexed


def write_snapshot(artists, output_root, captured_at):
    if captured_at.utcoffset() is None:
        raise ValueError("The capture timestamp needs a UTC offset.")
    captured_at = captured_at.astimezone(timezone.utc)
    records = [
        {
            "spotify_id": artist.get("id"),
            "name": artist.get("name"),
            "spotify_url": (artist.get("external_urls") or {}).get("spotify"),
            "genres": artist.get("genres"),
            "followers": (artist.get("followers") or {}).get("total"),
            "popularity": artist.get("popularity"),
        }
        for artist in artists
    ]
    index_artists(records)
    captured_at_text = captured_at.isoformat()
    snapshot = {
        "schema_version": SCHEMA_VERSION,
        "captured_at": captured_at_text,
        "artists": records,
    }
    directory = output_root / f"followed-artists-{captured_at:%Y%m%dT%H%M%S%fZ}"
    directory.mkdir(parents=True, exist_ok=False)
    with (directory / "artists.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=("captured_at", *ARTIST_FIELDS))
        writer.writeheader()
        for record in records:
            row = {**record, "captured_at": captured_at_text}
            if row["genres"] is not None:
                row["genres"] = json.dumps(row["genres"], ensure_ascii=False)
            name = row["name"]
            # Keep formula-like names from being evaluated when opened in a spreadsheet.
            if name.lstrip().startswith(("=", "+", "-", "@")) or name.startswith(("\t", "\r", "\n")):
                row["name"] = "'" + name
            writer.writerow(row)
    (directory / "artists.json").write_text(
        json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return directory


def read_snapshot(path):
    try:
        snapshot = json.loads(path.read_text(encoding="utf-8-sig"))
        if not isinstance(snapshot, dict) or snapshot.get("schema_version") != SCHEMA_VERSION:
            raise ValueError(f"Expected a followed-artist snapshot with schema version {SCHEMA_VERSION}.")
        captured_at = snapshot.get("captured_at")
        if not isinstance(captured_at, str):
            raise ValueError("Missing ISO 8601 capture timestamp.")
        if captured_at.endswith("Z"):
            captured_at = captured_at[:-1] + "+00:00"
        timestamp = datetime.fromisoformat(captured_at)
        if timestamp.utcoffset() is None:
            raise ValueError("The capture timestamp needs a UTC offset.")
        return timestamp, index_artists(snapshot.get("artists"))
    except (OSError, ValueError) as error:
        raise ValueError(f"{path}: {error}") from error


def describe_changes(previous, current):
    for label, ids, artists in (
        ("Followed", current.keys() - previous.keys(), current),
        ("Unfollowed", previous.keys() - current.keys(), previous),
    ):
        for spotify_id in sorted(ids, key=lambda key: (artists[key]["name"].casefold(), key)):
            yield f"  {label}: {artists[spotify_id]['name']} [{spotify_id}]"
    shared_ids = previous.keys() & current.keys()
    for spotify_id in sorted(shared_ids, key=lambda key: (current[key]["name"].casefold(), key)):
        before = previous[spotify_id].get("genres")
        after = current[spotify_id].get("genres")
        if before is None or after is None:
            continue
        added = sorted(set(after) - set(before))
        removed = sorted(set(before) - set(after))
        if added or removed:
            yield f"  Genres changed: {current[spotify_id]['name']} [{spotify_id}]"
            yield f"    Added: {', '.join(added) or 'none'}"
            yield f"    Removed: {', '.join(removed) or 'none'}"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("snapshots", type=Path, nargs="+", help="Two or more artists.json snapshots")
    args = parser.parse_args()
    if len(args.snapshots) < 2:
        parser.error("Supply at least two JSON snapshots.")
    try:
        snapshots = sorted((read_snapshot(path) for path in args.snapshots), key=lambda item: item[0])
    except ValueError as error:
        parser.error(str(error))
    timestamps = [timestamp for timestamp, _ in snapshots]
    if len(set(timestamps)) != len(timestamps):
        parser.error("Each snapshot must have a distinct capture timestamp.")
    for (before, previous), (after, current) in zip(snapshots, snapshots[1:]):
        print(f"{before.isoformat()} to {after.isoformat()}")
        changes = list(describe_changes(previous, current))
        print("\n".join(changes) or "  No follow or comparable genre changes observed.")


if __name__ == "__main__":
    main()
