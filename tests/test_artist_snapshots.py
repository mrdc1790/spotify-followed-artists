"""Exercise structured exports and the offline comparison command."""

from contextlib import redirect_stdout
import csv
from datetime import datetime, timezone
from io import StringIO
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from artist_snapshots import main, read_snapshot, write_snapshot


class SnapshotTests(unittest.TestCase):
    def test_snapshots_keep_ids_and_report_changes_at_each_capture(self):
        captures = [datetime(2026, 11, day, 12, tzinfo=timezone.utc) for day in (1, 2, 3)]
        same_name_old = {"id": "old", "name": "Same Name"}
        same_name_new = {"id": "new", "name": "Same Name"}
        tagged = {"id": "tagged", "name": '=Example, "Artist"', "genres": ["house", "disco"]}
        missing = {"id": "missing", "name": "Unknown Genres"}
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            before = write_snapshot([same_name_old, tagged, missing], root, captures[0])
            changed = write_snapshot([
                same_name_new, {**tagged, "genres": ["disco", "techno"]},
                {**missing, "genres": ["house"]},
            ], root, captures[1])
            unchanged = write_snapshot([
                same_name_new, {**tagged, "genres": ["techno", "disco"]},
                {**missing, "genres": ["house"]},
            ], root, captures[2])

            timestamp, records = read_snapshot(before / "artists.json")
            self.assertEqual(timestamp, captures[0])
            self.assertEqual(records["tagged"]["name"], tagged["name"])
            self.assertIsNone(records["missing"]["genres"])
            with (before / "artists.csv").open(encoding="utf-8-sig", newline="") as handle:
                rows = {row["spotify_id"]: row for row in csv.DictReader(handle)}
            self.assertEqual(rows["missing"]["genres"], "")
            self.assertEqual(rows["tagged"]["name"], "'" + tagged["name"])
            self.assertEqual(json.loads(rows["tagged"]["genres"]), tagged["genres"])
            self.assertEqual(rows["tagged"]["captured_at"], captures[0].isoformat())

            paths = [str(folder / "artists.json") for folder in (unchanged, before, changed)]
            with patch("sys.argv", ["artist_snapshots.py", *paths]), redirect_stdout(StringIO()) as out:
                main()
            report = out.getvalue()
            self.assertIn(f"{captures[0].isoformat()} to {captures[1].isoformat()}", report)
            self.assertIn("Followed: Same Name [new]", report)
            self.assertIn("Unfollowed: Same Name [old]", report)
            self.assertIn("Added: techno\n    Removed: house", report)
            self.assertNotIn("Unknown Genres", report)
            self.assertIn("No follow or comparable genre changes observed.", report)
            self.assertEqual(report.count("Genres changed:"), 1)

    def test_duplicate_ids_are_rejected_instead_of_discarding_records(self):
        with TemporaryDirectory() as temporary:
            path = Path(temporary) / "artists.json"
            path.write_text(json.dumps({
                "schema_version": 1,
                "captured_at": "2026-11-01T12:00:00Z",
                "artists": [
                    {"spotify_id": "same", "name": "First"},
                    {"spotify_id": "same", "name": "Second"},
                ],
            }), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Duplicate Spotify artist ID"):
                read_snapshot(path)
