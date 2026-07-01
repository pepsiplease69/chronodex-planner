#!/usr/bin/env python3
"""
gen_month.py <YEAR> <MONTH>

Generates one Chronodex page per day of the given month, then merges
them all into a single PDF: output/<YEAR>-<MM>-<MonthName>.pdf

Usage:
    python3 gen_month.py 2026 3
"""

import argparse
import calendar
import sys
from datetime import date, timedelta
from pathlib import Path

from pypdf import PdfWriter

from chronodex_letter import generate_page
from gen_cover import generate_cover

SCRIPT_DIR = Path(__file__).parent
PAGES_DIR  = SCRIPT_DIR / "pages"
OUTPUT_DIR = SCRIPT_DIR / "output"

DAY_NAMES   = ["Monday", "Tuesday", "Wednesday", "Thursday",
               "Friday", "Saturday", "Sunday"]
MONTH_ABBRS = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun",
               "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

WORK_DAYS = {"Monday", "Tuesday", "Wednesday", "Thursday"}


def generate_month(year, month):
    if not (1 <= month <= 12):
        sys.exit("Month must be 1–12.")

    PAGES_DIR.mkdir(exist_ok=True)
    OUTPUT_DIR.mkdir(exist_ok=True)

    month_name = calendar.month_name[month]
    num_days   = calendar.monthrange(year, month)[1]

    first_day = date(year, month, 1)
    last_day  = date(year, month, num_days)

    range_start = first_day - timedelta(days=first_day.weekday())
    range_end   = last_day  + timedelta(days=(3 - last_day.weekday()) % 7)
    if last_day.weekday() >= 3:
        range_end = last_day + timedelta(days=max(0, 3 - last_day.weekday()))

    page_files = []
    cursor = range_start
    while cursor <= range_end:
        day_str = DAY_NAMES[cursor.weekday()]

        if day_str not in WORK_DAYS:
            cursor += timedelta(days=1)
            continue

        day_abbr = MONTH_ABBRS[cursor.month]
        date_str = f"{day_abbr} {cursor.day}"
        out_file = PAGES_DIR / f"{cursor.year}-{cursor.month:02d}-{cursor.day:02d}.pdf"

        marker = "" if cursor.month == month else " ◂ overflow"
        print(f"  Generating {date_str} ({day_str}) → {out_file.name}{marker}")
        generate_page(str(out_file), date_str, day_str)

        page_files.append(out_file)
        cursor += timedelta(days=1)

    cover_file = PAGES_DIR / f"{year}-{month:02d}-cover.pdf"
    print(f"\n  Generating cover → {cover_file.name}")
    generate_cover(year, month, str(cover_file))

    merged_path = OUTPUT_DIR / f"{year}-{month:02d}-{month_name}.pdf"
    writer = PdfWriter()
    writer.append(str(cover_file))
    for pf in page_files:
        writer.append(str(pf))

    with open(merged_path, "wb") as f:
        writer.write(f)

    print(f"\n✓ cover + {len(page_files)} pages merged → {merged_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a full-month Chronodex PDF.")
    parser.add_argument("year",  type=int, help="e.g. 2026")
    parser.add_argument("month", type=int, help="1–12")
    args = parser.parse_args()
    generate_month(args.year, args.month)
