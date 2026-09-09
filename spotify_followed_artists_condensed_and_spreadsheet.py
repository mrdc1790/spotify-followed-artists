"""Convert a followed-artists export to a names list and formatted workbook."""

import argparse
import re
from pathlib import Path

from openpyxl import Workbook
from openpyxl.formatting.rule import ColorScaleRule
from openpyxl.styles import Font, PatternFill
from openpyxl.utils import get_column_letter


RECORD = re.compile(
    r"(?P<number>\d+)\. (?P<name>[^\n]+)\n"
    r"   Followers: (?P<followers>[\d,]+|N/A)\n"
    r"   Popularity: (?P<popularity>\d+|N/A)\n"
    r"   Genres: (?P<genres>[^\n]*)\n"
    r"   URL: (?P<url>https://open\.spotify\.com/artist/[^\s]+)"
)


def parse_export(content):
    content = content.replace("\r\n", "\n").strip()
    blocks = re.split(r"\n\s*\n", content)
    header = re.fullmatch(r"Total artists: (\d+)", blocks[0])
    if not header:
        raise ValueError("Missing 'Total artists: N' header.")
    artists = []
    for block in blocks[1:]:
        match = RECORD.fullmatch(block)
        if not match:
            raise ValueError(f"Malformed artist record {len(artists) + 1}.")
        artist = match.groupdict()
        artist["number"] = int(artist["number"])
        for field in ("followers", "popularity"):
            artist[field] = None if artist[field] == "N/A" else int(artist[field].replace(",", ""))
        artists.append(artist)
    if len(artists) != int(header[1]):
        raise ValueError("Artist count does not match the export header.")
    return artists


def convert_export(input_path):
    input_path = Path(input_path)
    artists = parse_export(input_path.read_text(encoding="utf-8-sig"))
    names_path = input_path.with_name(input_path.stem + "_names_only.txt")
    workbook_path = input_path.with_suffix(".xlsx")
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Spotify Artists"
    sheet.append(["#", "Artist", "Followers", "Popularity", "Genres", "Spotify URL"])
    for cell in sheet[1]:
        cell.fill = PatternFill("solid", fgColor="1DB954")
        cell.font = Font(bold=True, color="FFFFFF")
    for artist in artists:
        sheet.append([artist[field] for field in
                      ("number", "name", "followers", "popularity", "genres", "url")])
        # Artist-provided text must remain text, even when it starts with '='.
        for column in (2, 5, 6):
            sheet.cell(sheet.max_row, column).data_type = "s"
        sheet.cell(sheet.max_row, 3).number_format = "#,##0"
        link = sheet.cell(sheet.max_row, 6)
        link.hyperlink = link.value
        link.style = "Hyperlink"
    sheet.auto_filter.ref = sheet.dimensions
    sheet.freeze_panes = "A2"
    for column, width in enumerate((8, 35, 14, 12, 50, 60), 1):
        sheet.column_dimensions[get_column_letter(column)].width = width
    if artists:
        sheet.conditional_formatting.add(
            f"D2:D{sheet.max_row}",
            ColorScaleRule(start_type="min", start_color="FFF5F5",
                           mid_type="percentile", mid_value=50, mid_color="FFE599",
                           end_type="max", end_color="93C47D"),
        )
    workbook.save(workbook_path)
    names_path.write_text("".join(a["name"] + "\n" for a in artists), encoding="utf-8")
    return names_path, workbook_path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="Timestamped text export")
    args = parser.parse_args()
    try:
        paths = convert_export(args.input)
    except (OSError, ValueError) as error:
        parser.error(str(error))
    for path in paths:
        print(f"Created: {path}")


if __name__ == "__main__":
    main()
