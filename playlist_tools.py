"""Shared playlist planning; Spotify writes happen only after the full plan is ready."""

import argparse
from pathlib import Path

from spotify_common import create_client, unique_names


DEFAULT_ARTISTS = [
    "Porter Robinson", "ODESZA", "REZZ", "San Holo", "Flume", "Jai Wolf",
    "Haywyre", "Big Wild", "Virtual Riot", "Pretty Lights", "Illenium",
    "Seven Lions", "Louis The Child", "What So Not", "Mura Masa",
    "Cashmere Cat", "NGHTMRE", "TroyBoi", "Slushii", "Ekali",
    "Alison Wonderland", "Chet Porter", "Herobust", "Ganja White Night",
    "Ghastly", "Kayzo", "Whethan", "Petit Biscuit", "Gramatik", "TOKiMONSTA",
    "KRANE", "QUIX", "Tchami", "Malaa", "Hotel Garuda", "Boombox Cartel",
    "Carmack", "Minnesota", "CloZee", "MEMBA",
]


def collect_tracks(client, names, source="search", market="US"):
    uris = []
    for name in unique_names(names):
        results = client.search(q=name, type="artist", limit=10)["artists"]["items"]
        artist = next((a for a in results if a["name"].casefold() == name.casefold()), None)
        if artist is None:
            print(f"Skipped {name}: no exact artist-name match.")
            continue
        if source == "top":
            tracks = client.artist_top_tracks(artist["id"], country=market)["tracks"]
        else:
            query_name = artist["name"].replace('"', " ")
            tracks = client.search(
                q=f'artist:"{query_name}"', type="track", limit=10, market=market
            )["tracks"]["items"]
        matches = [t["uri"] for t in tracks if t.get("uri")
                   and t.get("is_playable") is not False
                   and any(a["id"] == artist["id"] for a in t.get("artists", []))]
        uris.extend(list(dict.fromkeys(matches))[:5])
    return list(dict.fromkeys(uris))


def create_playlist(client, name, uris, public=False):
    if not uris:
        raise ValueError("No matching tracks found; no playlist was created.")
    playlist = client.current_user_playlist_create(name, public=public)
    playlist_id = playlist["id"]
    print(f"Created playlist {playlist_id}; adding {len(uris)} tracks.")
    for offset in range(0, len(uris), 100):
        # Spotipy 2.26 sends a bare array here; the current endpoint requires an object.
        client._post(f"playlists/{playlist_id}/items", payload={"uris": uris[offset:offset + 100]})
    return playlist


def main(from_file=False):
    parser = argparse.ArgumentParser(description="Build a playlist from up to five tracks per artist.")
    if from_file:
        parser.add_argument("input", nargs="?", type=Path, default=Path("edm-artists.txt"))
        parser.add_argument("--include-defaults", action="store_true", help="Also include the built-in 40 artists")
    parser.add_argument("--name", default="Five Songs per Artist")
    parser.add_argument("--source", choices=("search", "top"), default="search",
                        help="Search results by default; top requires API access to artist top tracks")
    parser.add_argument("--market", default="US", help="Two-letter market code")
    parser.add_argument("--public", action="store_true", help="Create a public playlist")
    parser.add_argument("--dry-run", action="store_true", help="Resolve tracks without creating a playlist")
    args = parser.parse_args()
    if len(args.market) != 2 or not args.market.isalpha():
        parser.error("--market must be a two-letter country code")
    if not args.name.strip():
        parser.error("--name must not be empty")
    names = DEFAULT_ARTISTS
    if from_file:
        try:
            names = args.input.read_text(encoding="utf-8-sig").splitlines()
        except OSError as error:
            parser.error(str(error))
        if args.include_defaults:
            names += DEFAULT_ARTISTS
    if not unique_names(names):
        parser.error("The artist list is empty.")
    scope = "playlist-modify-public" if args.public else "playlist-modify-private"
    client = create_client(scope)
    uris = collect_tracks(client, names, args.source, args.market.upper())
    print(f"Resolved {len(uris)} unique tracks.")
    if args.dry_run:
        for uri in uris:
            print(uri)
        return
    playlist = create_playlist(client, args.name, uris, args.public)
    print(f"Saved {len(uris)} tracks: {playlist['external_urls']['spotify']}")
