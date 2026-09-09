"""Shared authentication and cursor pagination for command-line tools."""

import os

import spotipy
from spotipy.oauth2 import SpotifyOAuth


def create_client(scope):
    missing = [name for name in ("SPOTIPY_CLIENT_ID", "SPOTIPY_CLIENT_SECRET")
               if not os.environ.get(name)]
    if missing:
        raise SystemExit("Set these environment variables first: " + ", ".join(missing))
    return spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            redirect_uri=os.environ.get(
                "SPOTIPY_REDIRECT_URI", "http://127.0.0.1:8888/callback"
            ),
            scope=scope,
            cache_path=".spotify_cache",
            open_browser=True,
        ),
        requests_timeout=30,
    )


def followed_artists(client):
    """Yield all followed artists in API order, stopping at the last cursor."""
    after = None
    seen_cursors = set()
    while True:
        page = client.current_user_followed_artists(limit=50, after=after)["artists"]
        yield from page["items"]
        after = (page.get("cursors") or {}).get("after")
        if not page["items"] or not after:
            return
        if after in seen_cursors:
            raise RuntimeError("Spotify returned a repeated pagination cursor.")
        seen_cursors.add(after)


def unique_names(names):
    """Deduplicate names case-insensitively while preserving first spelling."""
    seen = set()
    result = []
    for name in names:
        name = name.strip()
        if name and name.casefold() not in seen:
            seen.add(name.casefold())
            result.append(name)
    return result
