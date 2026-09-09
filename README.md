# Spotify Followed Artists

Python command-line tools to export followed artists, explore their genres, build playlists, and review duplicate saved recordings.

## Setup

Use Python 3.10 or newer. From the project folder, create an environment and install the tested dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

On macOS/Linux, activate with `source .venv/bin/activate`. If PowerShell blocks activation, run `.\.venv\Scripts\python.exe` in place of `python`.

Create an app in the [Spotify developer dashboard](https://developer.spotify.com/dashboard) and register this exact redirect URI:

```text
http://127.0.0.1:8888/callback
```

Set credentials in your terminal session before running tools that access Spotify:

```powershell
$env:SPOTIPY_CLIENT_ID = "your-client-id"
$env:SPOTIPY_CLIENT_SECRET = "your-client-secret"
```

On macOS/Linux, use `export SPOTIPY_CLIENT_ID="..."` and `export SPOTIPY_CLIENT_SECRET="..."`. Optional `SPOTIPY_REDIRECT_URI` overrides the default callback. The scripts read environment variables directly; they do not load a `.env` file.

Authentication opens your browser and stores a local `.spotify_cache`. Credentials and token caches must stay out of Git. Importing the Python modules does not authenticate or change your account.

## Export and convert followed artists

```powershell
python spotify_followed_artists_list.py
python spotify_followed_artists_condensed_and_spreadsheet.py spotify_followed_artists_YYYYMMDD_HHMMSS.txt
```

Use the actual filename printed by the first command. The converter writes a names-only text file and an Excel workbook beside the input. The workbook includes links, filters, a frozen header, and popularity coloring when data is present.

The exporter preserves API order. `--reverse` reverses that order, but neither order represents verified follow dates. Unavailable follower counts and popularity appear as `N/A` in text and blank cells in Excel. Use `--output filename.txt` to select an export filename.

## Explore genres and artist names

```powershell
python electronic_artists_edm.py --output-dir output
python unique_artists.py output/different_genres.json --genre dubstep --output edm-artists.txt
python hipHopArtists.py Lil --output followed_artists.txt
```

- `electronic_artists_edm.py` groups **all** followed artists by genre. It writes `different_genres.json`, `genres.txt`, and `genres-refined.txt`. Artists may belong to multiple genres; deduplication happens within each genre.
- `unique_artists.py` reads that JSON mapping and writes deduplicated names as both text and JSON. `--genre` matches a genre substring without case sensitivity. Omit it to include every genre. The default output filename `edm-artists.txt` does not itself apply an EDM filter.
- `hipHopArtists.py` matches a name prefix, not a hip-hop genre. Its historical filename is retained.

The three genre files in the repository are a saved snapshot. The JSON and refined report were rebuilt from the supplied `genres.txt`; they are not live Spotify data. Running the genre exporter without `--output-dir` replaces the snapshots in the current directory.

## Build playlists

```powershell
python playlist-40-artists.py --dry-run
python playlist-40-artists.py --name "My Artist Mix"
python playlist-allEDM-artists.py edm-artists.txt --name "Dubstep Mix"
```

The first tool uses the built-in 40-artist list. The second reads one artist name per line; `--include-defaults` also adds the built-in list.

Both resolve up to five tracks per artist, skip artists without an exact name match, and remove duplicate track URIs. The default source is Spotify search results, **not a popularity ranking**. Artist names can be ambiguous; inspect `--dry-run` output before creating a playlist. Use `--market GB` to change the default US market.

Playlists are private unless `--public` is supplied. Each run without `--dry-run` creates a new playlist. All tracks are resolved before creation; a failure while adding batches can leave a partially filled playlist whose ID is printed.

`--source top` uses the legacy artist-top-tracks endpoint only if your app still has access. It fails before creating a playlist when Spotify denies that endpoint.

## Review duplicate saved recordings

```powershell
python unsaveDuplicates.py
python unsaveDuplicates.py --apply
```

The default command previews candidates. `--apply` prints the candidates and requires typing `yes` before removing extra versions from your saved library. Matching requires the same ISRC recording identifier and artist IDs; tracks missing those fields are skipped. The first version encountered is retained. This conservative rule can miss duplicates and should still be reviewed.

## Spotify API compatibility

These tools use Spotipy 2.26.0 and current playlist/library routes. Spotify's [February 2026 API changes](https://developer.spotify.com/documentation/web-api/references/changes/february-2026) remove artist top tracks and some statistics for affected apps. Account access and app quota mode can still limit which commands work. Playlist insertion uses a small compatibility call because this Spotipy version sends a bare array where the endpoint expects an object.

API errors are allowed to stop execution rather than silently publishing incomplete results. Live Spotify actions are not part of the automated tests.

## Development

```powershell
python -m unittest discover -s tests -v
```

The tests cover pagination, genre parsing, missing statistics, Excel output, playlist batching, safe imports, and duplicate detection without contacting Spotify.

The shared `spotify_common.py` and `playlist_tools.py` modules hold reusable logic. Existing PyCharm project configuration is included; local workspace settings, environments, caches, and new generated exports are ignored.
