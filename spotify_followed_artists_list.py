"""
Export all followed Spotify artists in FOLLOW ORDER (newest -> oldest).

IMPORTANT LIMITATION:
Spotify's API does NOT expose "date followed" for artists.

So this script can ONLY:
1. Fetch all followed artists
2. Preserve Spotify's returned order

Empirically, Spotify currently appears to return followed artists
roughly oldest -> newest for many users, but this is NOT guaranteed
or officially documented.

If you want actual historical follow timestamps, Spotify does not provide them.
"""

from spotipy.oauth2 import SpotifyOAuth
import spotipy
from datetime import datetime
import time
import os

# =========================================================
# CONFIG
# =========================================================

CLIENT_ID = os.environ["SPOTIPY_CLIENT_ID"]
CLIENT_SECRET = os.environ["SPOTIPY_CLIENT_SECRET"]
REDIRECT_URI = "http://127.0.0.1:8888/callback"

print("Starting OAuth...")

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope="user-follow-read",
    cache_path=".spotify_cache",
    open_browser=True
))

# =========================================================
# FETCH FOLLOWED ARTISTS
# =========================================================

artists = []

after = None
total = 0

while True:

    results = sp.current_user_followed_artists(limit=50, after=after)

    items = results["artists"]["items"]

    if not items:
        break

    for artist in items:
        artists.append({
            "name": artist["name"],
            "followers": artist["followers"]["total"],
            "genres": artist["genres"],
            "popularity": artist["popularity"],
            "url": artist["external_urls"]["spotify"]
        })

    total += len(items)

    print(f"Fetched {total} artists...")

    after = results["artists"]["cursors"]["after"]

    if len(items) < 50:
        break

    time.sleep(0.05)

# =========================================================
# SAVE
# =========================================================

# Spotify appears to return oldest -> newest for many users,
# but this is NOT officially guaranteed.
artists.reverse()

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f"spotify_followed_artists_{timestamp}.txt"

with open(filename, "w", encoding="utf-8") as f:

    f.write(f"Total artists: {len(artists)}\n\n")

    for i, artist in enumerate(artists, start=1):

        f.write(f"{i}. {artist['name']}\n")
        f.write(f"   Followers: {artist['followers']:,}\n")
        f.write(f"   Popularity: {artist['popularity']}\n")
        f.write(f"   Genres: {', '.join(artist['genres'])}\n")
        f.write(f"   URL: {artist['url']}\n\n")

print(f"\nSaved to {filename}")
