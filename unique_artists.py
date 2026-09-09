"""Extract unique names from a genre-to-artists JSON mapping."""

import argparse
import json
from pathlib import Path

from spotify_common import unique_names


def extract_names(data, genre_filter=None):
    if not isinstance(data, dict) or any(
        not isinstance(names, list) or any(not isinstance(name, str) for name in names)
        for names in data.values()
    ):
        raise ValueError("Expected a JSON object mapping genres to lists of artist names.")
    return sorted(unique_names(
        name for genre, names in data.items()
        if genre_filter is None or genre_filter.casefold() in genre.casefold()
        for name in names
    ), key=str.casefold)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", nargs="?", type=Path, default=Path("different_genres.json"))
    parser.add_argument("--genre", help="Include only genres containing this text")
    parser.add_argument("--output", type=Path, default=Path("edm-artists.txt"))
    args = parser.parse_args()
    if args.output.suffix.lower() != ".txt":
        parser.error("--output must end in .txt")
    try:
        names = extract_names(json.loads(args.input.read_text(encoding="utf-8-sig")), args.genre)
    except (OSError, ValueError) as error:
        parser.error(str(error))
    args.output.write_text("".join(name + "\n" for name in names), encoding="utf-8")
    args.output.with_suffix(".json").write_text(
        json.dumps(names, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Saved {len(names)} names to {args.output} and {args.output.with_suffix('.json')}")


if __name__ == "__main__":
    main()
