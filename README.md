# Spotify Projects

Python scripts for exporting the artists you follow on Spotify and converting the export into a names-only list and a formatted Excel workbook.

## Scripts

- `spotify_followed_artists_list.py` authenticates with Spotify and exports artist names, follower counts, popularity, genres, and Spotify links to a timestamped text file.
- `spotify_followed_artists_condensed_and_spreadsheet.py` converts that text file into a names-only text file and an `.xlsx` workbook with clickable links, filters, a frozen header, and popularity color formatting.

## Setup

Install Python 3, then run these commands from the project folder:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Create a Spotify developer app and configure its redirect URI as `http://127.0.0.1:8888/callback`.
Set your app credentials in the current PowerShell session:

```powershell
$env:SPOTIPY_CLIENT_ID = "your-client-id"
$env:SPOTIPY_CLIENT_SECRET = "your-client-secret"
```

Do not put real credentials in the source code or commit OAuth cache files.

## Export followed artists

```powershell
.\.venv\Scripts\python.exe spotify_followed_artists_list.py
```

Complete the browser authorization when prompted. The script requests the `user-follow-read` scope and saves an export such as `spotify_followed_artists_20260909_120000.txt` in the current directory.

## Create the list and spreadsheet

Open `spotify_followed_artists_condensed_and_spreadsheet.py` and set `INPUT_FILE` to the filename produced by the export script. Then run:

```powershell
.\.venv\Scripts\python.exe spotify_followed_artists_condensed_and_spreadsheet.py
```

This creates `<export-name>_names_only.txt` and `<export-name>.xlsx` in the current directory.

## Limitations

The exporter reverses the order returned by Spotify. Do not treat this as a reliable follow-date ordering: the export contains no historical follow timestamps. Both scripts expect the response and text formats shown in the source; they do not currently recover from missing fields or malformed input.

Generated exports, local environments, and authentication caches are excluded from Git.
