"""Preview duplicate saved recordings and optionally unsave extra versions."""

import argparse

from spotify_common import create_client


def saved_tracks(client):
    offset = 0
    while True:
        page = client.current_user_saved_tracks(limit=50, offset=offset)
        items = page["items"]
        for item in items:
            track = item.get("track")
            if track and track.get("id") and not track.get("is_local"):
                yield track
        if not items or not page.get("next"):
            return
        offset += len(items)


def find_duplicates(tracks):
    """Keep the first version; require a recording ID and matching artists."""
    seen_ids = set()
    recordings = set()
    duplicates = []
    for track in tracks:
        track_id = track["id"]
        if track_id in seen_ids:
            continue
        seen_ids.add(track_id)
        isrc = (track.get("external_ids") or {}).get("isrc")
        artist_ids = tuple(sorted(a["id"] for a in track.get("artists", []) if a.get("id")))
        if not isrc or not artist_ids:
            continue
        key = (isrc.upper(), artist_ids)
        if key in recordings:
            duplicates.append(track)
        else:
            recordings.add(key)
    return duplicates


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="Confirm and remove duplicates")
    args = parser.parse_args()
    scope = "user-library-read" + (" user-library-modify" if args.apply else "")
    client = create_client(scope)
    duplicates = find_duplicates(saved_tracks(client))
    for track in duplicates:
        print(f"{track['name']} - {', '.join(a['name'] for a in track['artists'])} ({track['id']})")
    print(f"{len(duplicates)} duplicate saved tracks found.")
    if not duplicates or not args.apply:
        return
    if input("Unsave these tracks? Type yes to confirm: ").strip().casefold() != "yes":
        print("Aborted.")
        return
    ids = [track["id"] for track in duplicates]
    for offset in range(0, len(ids), 50):
        client.current_user_saved_tracks_delete(ids[offset:offset + 50])
    print(f"Removed {len(ids)} saved tracks.")


if __name__ == "__main__":
    main()
